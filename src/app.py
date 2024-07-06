import asyncio

from github.PullRequest import PullRequest

import ai.assistant
import ai.tool
import code.pull_request
import logger
import model


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
        if not review_request.diff:
            return []

        # Stagger request start times to comply with rate limits
        logger.log.debug(f"Waiting {delay} seconds before reviewing")
        await asyncio.sleep(delay)

        file_comments = await self._assistant.review_file(review_request)

        return file_comments

    async def _review_files(
            self,
            review_requests: list[model.FileReviewRequest],
    ) -> list[model.Comment]:
        return [
            comment
            for file_comments in await asyncio.gather(*[
                asyncio.create_task(self._review_file(req, delay=i * 3.5))
                for i, req in enumerate(review_requests)
            ])
            for comment in file_comments
        ]

    async def run(self):
        review_requests = await self._assistant.request_reviews(self._context)
        logger.log.debug(
            f"Files to review: \n"
            f"- {"\n- ".join([r.path for r in review_requests])}"
        )

        comments = await self._review_files(review_requests)

        feedback = await self._assistant.get_feedback(comments)
        logger.log.info(f"Overall Feedback: {feedback.evaluation}")

        if self._debug:
            logger.log.debug("Running in debug, no review submitted")
            return

        code.pull_request.submit_review(self._pr, feedback)
