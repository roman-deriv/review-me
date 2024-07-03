import github
import logging
from github.PullRequest import PullRequest

import ai.assistant
import ai.prompt
import ai.tool
import config
import model


logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('review-me.log'), logging.StreamHandler()])

logger = logging.getLogger(__name__)


def get_pr(cfg: config.GitHubConfig):
    logger.debug("get_pr start")
    gh = github.Github(cfg.token)
    repo = gh.get_repo(cfg.repository)
    pr = repo.get_pull(cfg.pr_number)
    logger.debug("get_pr finish")
    return pr


def build_context(pull_request: PullRequest) -> model.ReviewContext:
    logger.debug("build_context start")
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
    logger.debug("build_context finish")
    return context


class App:
    def __init__(self, app_config: config.AppConfig):
        logger.debug("creating App start")
        self._config = app_config
        self._pr = get_pr(self._config.github)

        context = build_context(self._pr)
        builder = ai.prompt.Builder(context)
        self._assistant = ai.assistant.Assistant(app_config.llm.model, builder)
        logger.debug("creating App finish")

    def _generate_feedback(self) -> model.Feedback:
        logger.debug("generate_feedback start")
        review_requests = self._assistant.files_to_review()

        comments: list[model.Comment] = []
        logger.info("Files being reviewed:")
        for req in review_requests:
            logger.info("Filename: %s", req.path)
            logger.info("Reason: %s", req.reason)

            file_comments = self._assistant.review_file(req.path)
            for comment in file_comments:
                logger.info("Comment: %s", comment)

            comments += file_comments

        feedback = self._assistant.get_feedback(comments)
        logger.info("OVERALL FEEDBACK: %s", feedback)
        logger.debug("generate_feedback finish")
        return feedback

    def _submit_review(self, feedback: model.Feedback):
        logger.debug("_submit_review start")
        if self._config.debug:
            logger.debug("_submit_review finish debug return")
            return

        self._pr.create_review(
            body=feedback.overall_comment,
            comments=feedback.comments,
            event="COMMENT",
        )
        logger.debug("_submit_review finish")

    def run(self):
        logger.debug("run start")
        feedback = self._generate_feedback()
        self._submit_review(feedback)
        logger.debug("run finish")
