import github
from github.PullRequest import PullRequest

import ai.assistant
import ai.prompt
import ai.tool
import config
import model
import logs


def get_pr(cfg: config.GitHubConfig):
    logs.debug("Fetching pull request")
    gh = github.Github(cfg.token)
    repo = gh.get_repo(cfg.repository)
    pr = repo.get_pull(cfg.pr_number)
    logs.debug("Pull request retrieved")
    return pr


def build_context(pull_request: PullRequest) -> model.ReviewContext:
    logs.debug("Building context")
    files = pull_request.get_files()
    context = model.ReviewContext(
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
    logs.debug("Context built sucessfully")
    return context


class App:
    def __init__(self, app_config: config.AppConfig):
        logs.debug("Creating App")
        self._config = app_config
        self._pr = get_pr(self._config.github)

        context = build_context(self._pr)
        builder = ai.prompt.Builder(context)
        self._assistant = ai.assistant.Assistant(app_config.llm.model, builder)
        logs.debug("Successfully created App")

    def _generate_feedback(self) -> model.Feedback:
        logs.debug("Starting to generating feedback")
        review_requests = self._assistant.files_to_review()

        comments: list[model.Comment] = []
        logs.info("Starting to review files")
        for req in review_requests:

            file_comments = self._assistant.review_file(req.path)
            for comment in file_comments:
                logs.info(f"Filename: {req.path}\nReason: {req.reason}\nComment: {comment}")

            comments += file_comments

        feedback = self._assistant.get_feedback(comments)
        logs.info(f"Overall Feedback: {feedback}")
        logs.debug("Finished generating feedback")
        return feedback

    def _submit_review(self, feedback: model.Feedback):
        logs.debug("Starting to submit review")
        if self._config.debug:
            logs.debug("Running in debug, no review submitted")
            return

        self._pr.create_review(
            body=feedback.overall_comment,
            comments=feedback.comments,
            event="COMMENT",
        )
        logs.debug("Submitted review")

    def run(self):
        logs.debug("Run started")
        feedback = self._generate_feedback()
        self._submit_review(feedback)
        logs.debug("Run finished")
