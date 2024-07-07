import code.model
import code.review.comment
import code.review.context
import code.review.model
import logger
from . import prompt, schema
from .anthropic import tool_completion
from .tool import TOOLS


class Assistant:
    def __init__(self, model_name: str, builder: prompt.Builder):
        self._model_name = model_name
        self._builder = builder

    async def request_reviews(
            self,
            context: code.review.model.PullRequestContextModel,
    ) -> list[code.review.model.FileContextModel]:
        results: schema.ReviewRequestsResponseModel = await tool_completion(
            system_prompt=self._builder.render_template(
                name="overview",
                prefix="system",
            ),
            prompt=self._builder.render_template(
                name="overview",
                prefix="user",
            ),
            model=self._model_name,
            tools=[TOOLS["review_files"]],
            tool_override="review_files",
        )

        return code.review.context.build_file_contexts(
            requests=results,
            context=context,
        )

    async def review_file(
            self,
            context: code.review.model.FileContextModel,
            severity_limit: int = code.model.Severity.OPTIONAL,
    ) -> list[code.model.GitHubCommentModel]:
        logger.log.debug(f"Reviewing file: {context.path}")
        logger.log.debug(f"Hunks: {context.patch.hunks}")

        file_review: schema.FileReviewResponseModel = await tool_completion(
            system_prompt=self._builder.render_template(
                name="file-review",
                prefix="system",
            ),
            prompt=self._builder.render_template(
                name="file-review",
                prefix="user",
                file_context=context,
            ),
            model=self._model_name,
            tools=[TOOLS["post_feedback"]],
            tool_override="post_feedback",
        )

        return code.review.comment.extract_comments(
            response=file_review,
            file_context=context,
            severity_limit=severity_limit,
        )

    async def get_feedback(
            self,
            comments: list[code.model.GitHubCommentModel],
    ) -> code.review.model.Feedback:
        response: schema.ReviewResponseModel = await tool_completion(
            system_prompt=self._builder.render_template(
                name="review-summary",
                prefix="system",
            ),
            prompt=self._builder.render_template(
                name="review-summary",
                prefix="user",
                comments=comments,
            ),
            model=self._model_name,
            tools=[TOOLS["submit_review"]],
            tool_override="submit_review",
        )

        return code.review.comment.parse_feedback(
            response=response,
            comments=comments,
        )
