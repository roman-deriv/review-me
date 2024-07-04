import asyncio

import github
from github.PullRequest import PullRequest

import ai.assistant
import ai.tool
import config
import logger
import model


def get_pr(cfg: config.GitHubConfig):
    gh = github.Github(cfg.token)
    repo = gh.get_repo(cfg.repository)
    pr = repo.get_pull(cfg.pr_number)
    logger.log.debug(f"Pull request retrieved: {pr.number}")
    return pr


def build_context(pull_request: PullRequest) -> model.ReviewContext:
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
    logger.log.debug(f"Context built sucessfully: {context.title}")
    return context


class App:
    def __init__(
            self,
            pull_request: PullRequest,
            assistant: ai.assistant.Assistant,
            debug: bool = False,
    ):
        self._pr = pull_request
        self._assistant = assistant
        self._debug = debug

    async def _review_file(
            self,
            review_request: model.FileReviewRequest,
            delay: float,
    ) -> list[model.Comment]:
        # Stagger request start times to comply with rate limits
        await asyncio.sleep(delay)

        file_comments = await self._assistant.review_file(review_request)

        logger.log.debug(f"File comments:")
        for comment in file_comments:
            logger.log.debug(comment)

        return file_comments

    async def _generate_feedback(self) -> model.Feedback:
        review_requests = await self._assistant.files_to_review()

        tasks = [
            asyncio.create_task(self._review_file(req, delay=i * 1.7))
            for i, req in enumerate(review_requests)
        ]

        file_reviews = await asyncio.gather(*tasks)

        comments: list[model.Comment] = [
            comment
            for file_comments in file_reviews
            for comment in file_comments
        ]

        feedback = await self._assistant.get_feedback(comments)
        logger.log.debug(f"Overall Feedback: {feedback}")
        return feedback

    def _submit_review(self, feedback: model.Feedback):
        if self._debug:
            logger.log.debug("Running in debug, no review submitted")
            return

        self._pr.create_review(
            body=feedback.overall_comment,
            comments=feedback.comments,
            event="COMMENT",
        )

    async def run(self):
        feedback = await self._generate_feedback()
        self._submit_review(feedback)
