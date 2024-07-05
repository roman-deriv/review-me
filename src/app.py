import asyncio

from github.PullRequest import PullRequest

import ai.assistant
import ai.tool
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

    async def _generate_feedback(self) -> model.Feedback:
        review_requests = await self._assistant.files_to_review(self._context)

        tasks = [
            asyncio.create_task(self._review_file(req, delay=i * 3.5))
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
