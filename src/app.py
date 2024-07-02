import github
from github.PullRequest import PullRequest

import ai.assistant
import ai.prompt
import ai.tool
import config
import model


def get_pr(cfg: config.GitHubConfig):
    gh = github.Github(cfg.token)
    repo = gh.get_repo(cfg.repository)
    return repo.get_pull(cfg.pr_number)


def build_context(pull_request: PullRequest) -> model.ReviewContext:
    return model.ReviewContext(
        title=pull_request.title,
        description=pull_request.body,
        commit_messages=[
            commit.commit.message
            for commit in pull_request.get_commits()
        ],
        review_comments=[
            comment.body
            for comment in pull_request.get_review_comments()
        ],
        issue_comments=[
            comment.body
            for comment in pull_request.get_issue_comments()
        ],
        diffs={
            file.filename: file.patch
            for file in pull_request.get_files()
        }
    )


class App:
    def __init__(self, app_config: config.AppConfig):
        self._config = app_config
        self._pr = get_pr(self._config.github)

        context = build_context(self._pr)
        builder = ai.prompt.Builder(context)
        self._assistant = ai.assistant.Assistant(app_config.llm.model, builder)

    def _generate_feedback(self) -> model.Feedback:
        files = self._assistant.files_to_review()

        comments: list[dict[str, str]] = []
        print("We should review these files")
        for file in files:
            print("Filename:", file["filename"])
            print("Reason:", file["reason"])
            print()
            filename = file["filename"]

            results = self._assistant.review_file(filename)

            comments = results["feedback"]
            for comment in comments:
                comment.update(path=filename)
                print(comment)
                print("--------")

            comments += comments

        review_summary = self._assistant.get_feedback(comments)
        overall_comment = review_summary["feedback"]
        evaluation = review_summary["event"]
        print()
        print("OVERALL FEEDBACK")
        print()
        print(overall_comment)
        print(evaluation)

        return model.Feedback(
            comments=comments,
            overall_comment=overall_comment,
            evaluation=evaluation,
        )

    def _submit_review(self, feedback: model.Feedback):
        if self._config.debug:
            return

        self._pr.create_review(
            body=feedback.overall_comment,
            comments=feedback.comments,
            event="COMMENT",
        )

    def run(self):
        feedback = self._generate_feedback()
        self._submit_review(feedback)
