import code.model
import code.review.comment
import code.review.model
import logger
from . import prompt, schema
from .anthropic import tool_completion
from .tool import TOOLS


class Assistant:
    def __init__(self, model_name: str, builder: prompt.Builder):
        self._model_name = model_name
        self._builder = builder

    async def overview(
            self,
            context: code.model.PullRequestContextModel,
    ) -> code.review.model.OverviewModel:
        completion = await tool_completion(
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
        response = schema.ReviewRequestsResponseModel(**completion)

        return code.review.comment.parse_overview(
            response=response,
            context=context,
        )

    async def review_file(
            self,
            observations: list[code.review.model.ObservationModel],
            context: code.review.model.FileContextModel,
            severity_limit: int = code.model.Severity.OPTIONAL,
    ) -> list[code.model.GitHubCommentModel]:
        logger.log.debug(f"Reviewing file: {context.path}")
        logger.log.debug(f"Hunks: {context.patch.hunks}")

        completion = await tool_completion(
            system_prompt=self._builder.render_template(
                name="file-review",
                prefix="system",
            ),
            prompt=self._builder.render_template(
                name="file-review",
                prefix="user",
                observations=observations,
                file_context=context,
            ),
            model=self._model_name,
            tools=[TOOLS["post_feedback"]],
            tool_override="post_feedback",
        )
        response = schema.FileReviewResponseModel(**completion)

        return code.review.comment.extract_comments(
            response=response,
            file_context=context,
            severity_limit=severity_limit,
        )

    async def get_feedback(
            self,
            comments: list[code.model.GitHubCommentModel],
    ) -> code.review.model.Feedback:
        completion = await tool_completion(
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
        response = schema.ReviewResponseModel(**completion)

        return code.review.comment.parse_feedback(
            response=response,
            comments=comments,
        )
