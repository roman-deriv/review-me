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
    logger.log.debug(f"Pull request retrieved: #{pr.number}")
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
    logger.log.debug(f"Context built successfully: {context.title}")
    return context


class App:
    def __init__(
            self,
            pull_request: PullRequest,
            context: model.ReviewContext,
            assistant: ai.assistant.Assistant,
            debug: bool = False,
    ):
        self._pr = pull_request
        self._context = context
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

        return file_comments

    async def _generate_feedback(self) -> model.Feedback:
        review_requests = await self._assistant.files_to_review(self._context)

        tasks = [
            asyncio.create_task(self._review_file(req, delay=i * 3))
            for i, req in enumerate(review_requests)
        ]

        file_reviews = await asyncio.gather(*tasks)

        comments: list[model.Comment] = [
            comment
            for file_comments in file_reviews
            for comment in file_comments
        ]

        feedback = await self._assistant.get_feedback(comments)
        logger.log.info(f"Overall Feedback: {feedback.evaluation}")
        return feedback

    def _submit_review(self, feedback: model.Feedback):
        if self._debug:
            logger.log.debug("Running in debug, no review submitted")
            return

        self._pr.create_review(
            body=f"{feedback.summary}\n\n"
                 f"{feedback.overall_comment}\n\n"
                 f"{feedback.evaluation}",
            comments=feedback.comments,
            event="COMMENT",
        )

    async def run(self):
        feedback = await self._generate_feedback()
        self._submit_review(feedback)
