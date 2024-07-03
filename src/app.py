import github
from github.PullRequest import PullRequest

import ai.assistant
import ai.prompt
import ai.tool
import config
import model
import logs


def get_pr(cfg: config.GitHubConfig):
    logs.debug("get_pr start")
    gh = github.Github(cfg.token)
    repo = gh.get_repo(cfg.repository)
    pr = repo.get_pull(cfg.pr_number)
    logs.debug("get_pr finish")
    return pr


def build_context(pull_request: PullRequest) -> model.ReviewContext:
    logs.debug("build_context start")
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
    logs.debug("build_context finish")
    return context


class App:
    def __init__(self, app_config: config.AppConfig):
        logs.debug("creating App start")
        self._config = app_config
        self._pr = get_pr(self._config.github)

        context = build_context(self._pr)
        builder = ai.prompt.Builder(context)
        self._assistant = ai.assistant.Assistant(app_config.llm.model, builder)
        logs.debug("creating App finish")

    def _generate_feedback(self) -> model.Feedback:
        logs.debug("generate_feedback start")
        review_requests = self._assistant.files_to_review()

        comments: list[model.Comment] = []
        logs.info("Files being reviewed:")
        for req in review_requests:
            logs.info(f"Filename: {req.path}")
            logs.info(f"Reason: {req.reason}")

            file_comments = self._assistant.review_file(req.path)
            for comment in file_comments:
                logs.info(f"Comment: {comment}")

            comments += file_comments

        feedback = self._assistant.get_feedback(comments)
        logs.info(f"OVERALL FEEDBACK: {feedback}")
        logs.debug("generate_feedback finish")
        return feedback

    def _submit_review(self, feedback: model.Feedback):
        logs.debug("_submit_review start")
        if self._config.debug:
            logs.debug("_submit_review finish debug return")
            return

        self._pr.create_review(
            body=feedback.overall_comment,
            comments=feedback.comments,
            event="COMMENT",
        )
        logs.debug("_submit_review finish")

    def run(self):
        logs.debug("run start")
        feedback = self._generate_feedback()
        self._submit_review(feedback)
        logs.debug("run finish")
