import asyncio

from github.PullRequest import PullRequest

import ai.assistant
import ai.tool
import code.model
import code.pull_request
import code.review.model
import logger


class App:
    def __init__(
            self,
            pull_request: PullRequest,
            context: code.review.model.PullRequestContextModel,
            assistant: ai.assistant.Assistant,
            debug: bool = False,
    ):
        self._pr = pull_request
        self._context = context
        self._assistant = assistant
        self._debug = debug

    async def _review_file(
            self,
            context: code.review.model.FileContextModel,
            delay: float,
    ) -> list[code.model.GitHubCommentModel]:
        if not context.patch.diff:
            return []

        # Stagger request start times to comply with rate limits
        logger.log.debug(f"Waiting {delay} seconds before reviewing")
        await asyncio.sleep(delay)

        file_comments = await self._assistant.review_file(context)

        return file_comments

    async def _review_files(
            self,
            contexts: list[code.review.model.FileContextModel],
    ) -> list[code.model.GitHubCommentModel]:
        return [
            comment
            for file_comments in await asyncio.gather(*[
                asyncio.create_task(self._review_file(context, delay=i * 5))
                for i, context in enumerate(contexts)
            ])
            for comment in file_comments
        ]

    async def run(self):
        file_contexts = await self._assistant.request_reviews(self._context)
        logger.log.debug(
            f"Files to review: \n"
            f"- {"\n- ".join([context.path for context in file_contexts])}"
        )

        comments = await self._review_files(file_contexts)

        feedback = await self._assistant.get_feedback(comments)
        logger.log.info(f"Overall Feedback: {feedback.evaluation}")

        if self._debug:
            logger.log.debug("Running in debug, no review submitted")
            return

        code.pull_request.submit_review(self._pr, feedback)
