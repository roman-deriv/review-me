import code.review
import logger
import model
from . import prompt, schema
from .anthropic import tool_completion
from .tool import TOOLS


class Assistant:
    def __init__(self, model_name: str, builder: prompt.Builder):
        self._model_name = model_name
        self._builder = builder

    async def request_reviews(
            self,
            context: model.ReviewContext,
    ) -> list[model.FileReviewRequest]:
        system_prompt = self._builder.render_template(
            name="overview",
            prefix="system",
        )
        results: schema.ReviewRequestsResponseModel = await tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.render_template(
                name="overview",
                prefix="user",
            ),
            model=self._model_name,
            tools=[TOOLS["review_files"]],
            tool_override="review_files",
        )

        return code.review.parse_review_requests(
            requests=results,
            context=context,
        )

    async def review_file(
            self,
            review_request: model.FileReviewRequest,
            severity_limit: int = model.Severity.OPTIONAL,
    ) -> list[model.Comment]:
        logger.log.debug(f"Reviewing file: {review_request.path}")

        system_prompt = self._builder.render_template(
            name="file-review",
            prefix="system",
        )

        logger.log.debug(f"Hunks: {review_request.hunks}")

        file_review = await tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.render_template(
                name="file-review",
                prefix="user",
                review_request=review_request,
            ),
            model=self._model_name,
            tools=[TOOLS["post_feedback"]],
            tool_override="post_feedback",
        )

        return code.review.parse_review(
            review=file_review,
            review_request=review_request,
            severity_limit=severity_limit,
        )

    async def get_feedback(
            self,
            comments: list[model.Comment],
    ) -> model.Feedback:
        system_prompt = self._builder.render_template(
            name="review-summary",
            prefix="system",
        )
        feedback = await tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.render_template(
                name="review-summary",
                prefix="user",
                comments=comments,
            ),
            model=self._model_name,
            tools=[TOOLS["submit_review"]],
            tool_override="submit_review",
        )

        return code.review.parse_feedback(
            feedback=feedback,
            comments=comments,
        )
