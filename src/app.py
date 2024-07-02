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
    files = pull_request.get_files()
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
            for file in files
        },
        added_files=[file.filename for file in files if file.status == 'added'],
        modified_files=[file.filename for file in files if file.status == 'modified'],
        deleted_files=[file.filename for file in files if file.status == 'removed']
    )


class App:
    def __init__(self, app_config: config.AppConfig):
        self._config = app_config
        self._pr = get_pr(self._config.github)

        context = build_context(self._pr)
        builder = ai.prompt.Builder(context)
        self._assistant = ai.assistant.Assistant(app_config.llm.model, builder)

    def _generate_feedback(self) -> model.Feedback:
        review_requests = self._assistant.files_to_review()

        comments: list[model.Comment] = []
        print("We should review these files")
        for req in review_requests:
            print("Filename:", req.path)
            print("Reason:", req.reason)
            print()

            file_comments = self._assistant.review_file(req.path)
            for comment in file_comments:
                print(comment)
                print("--------")

            comments += file_comments

        feedback = self._assistant.get_feedback(comments)
        print()
        print("OVERALL FEEDBACK")
        print()
        print(feedback)
        return feedback

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
