import dataclasses

import github
from github.PullRequest import PullRequest

import ai.prompt
import ai.service
import config


def files_to_review(pr: PullRequest):
    ctx_builder = ReviewContextBuilder(pull_request=pr)
    files = []

    return pr.get_files()


def generate_file_comments(pr, strategy, model, debug=False):
    chat_completion = ai.service.chat_completion(strategy)
    system_prompt = ai.prompt.load("system-prompt-code-file")
    commit_msgs = [commit.commit.message for commit in pr.get_commits()]

    file_comments = {}
    for file in files_to_review(pr):
        if file.status != "modified":
            continue
        prompt = (
            f"PR Title: {pr.title}\n\n"
            f"PR Commits: - {"\n- ".join(commit_msgs)}\n\n"
            f"PR Body:\n{pr.body}\n\n"
            f"Filename: {file.filename}\n\n"
            f"Diff:\n{file.patch}"
        )
        if debug:
            continue
        comment = chat_completion(system_prompt, prompt, model)
        file_comments[file.filename] = comment
    return file_comments


def get_pr(github_token, repo, pr_number):
    gh = github.Github(github_token)
    repo = gh.get_repo(repo)
    pr = repo.get_pull(pr_number)
    return pr


def get_pr_comments(pr: PullRequest):
    issue_comments = pr.get_issue_comments()
    review_comments = pr.get_review_comments()
    return issue_comments, review_comments


@dataclasses.dataclass
class Review:
    comments: dict[str, str]
    overall_comment = str


class ReviewContextBuilder:
    def __init__(self, pull_request: PullRequest):
        self._pr = pull_request

    def _pr_commits(self):
        return [
            commit.commit.message
            for commit in self._pr.get_commits()
        ]

    def _pr_diff(self):
        return {
            file.filename: file.patch
            for file in self._pr.get_files()
        }

    def _pr_comments(self) -> list:
        issue_comments = self._pr.get_issue_comments()
        review_comments = self._pr.get_review_comments()
        return [comment for comment in review_comments]

    def build(self) -> str:
        title = self._pr.title
        description = self._pr.body
        commit_messages = self._pr_commits()
        diff = self._pr_diff()

        return (
            f"PR Title: {title}\n\n"
            f"PR Body:\n{description}\n\n"
            f"PR Commits:\n- {"\n- ".join(commit_messages)}\n\n"
            f"Diff:\n{diff}"
        )


class App:
    def __init__(self, app_config: config.AppConfig):
        self._config = app_config

        self._pr = get_pr(
            self._config.github.token,
            self._config.github.repository,
            self._config.github.pr_number,
        )

    def _generate_review(self, comments: dict) -> Review:
        pass

    def _submit_review(self, review: Review):
        for filename, comment in review.comments.items():
            print(filename)
            print("--------")
            print(comment)
            print("========")
            print()
            if self._config.debug:
                continue

            self._pr.create_review_comment(comment)

    def run(self):
        comments = generate_file_comments(
            self._pr,
            self._config.llm.strategy,
            self._config.llm.model,
            debug=self._config.debug,
        )
        review = self._generate_review(comments)
        self._submit_review(review)


def main():
    cfg = config.from_env()
    app = App(cfg)
    app.run()


if __name__ == "__main__":
    main()
