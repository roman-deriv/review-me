import typing
from enum import IntEnum

import code.diff
import logger
import model
import review
from . import prompt
from .anthropic import tool_completion
from .tool import TOOLS


async def single_tool_query(
        prompt_name: str,
        tool_name: str,
        model_name: str,
        builder: prompt.Builder,
) -> dict[str, typing.Any]:
    return await tool_completion(
        system_prompt=builder.render_template(
            name=prompt_name,
            prefix="system",
        ),
        prompt=builder.render_template(
            name=prompt_name,
            prefix="user",
        ),
        model=model_name,
        tools=[TOOLS[tool_name]],
        tool_override=tool_name,
    )


class Severity(IntEnum):
    CRITICAL = 0
    MAJOR = 1
    OPTIONAL = 2
    MINOR = 3
    NO_CHANGE = 4

    @classmethod
    def from_string(cls, s):
        return cls[s.upper()]


class Assistant:
    def __init__(self, model_name: str, builder: prompt.Builder):
        self._model_name = model_name
        self._builder = builder

    async def request_reviews(
            self,
            context: model.ReviewContext,
    ) -> list[model.FileReviewRequest]:
        results = await single_tool_query(
            prompt_name="overview",
            tool_name="review_files",
            model_name=self._model_name,
            builder=self._builder,
        )

        files = [
            review.parse_review_request(req, context)
            for req in results.get("files", [])
        ]
        return files

    async def review_file(
            self,
            review_request: model.FileReviewRequest,
            severity_limit: int = Severity.OPTIONAL,
    ) -> list[model.Comment]:
        logger.log.debug(f"Reviewing file: {review_request.path}")
        logger.log.debug(f"Hunks: {review_request.hunks}")

        results = await single_tool_query(
            prompt_name="file-review",
            tool_name="post_feedback",
            model_name=self._model_name,
            builder=self._builder,
        )

        comments = []
        for comment in results["feedback"]:
            severity = Severity.from_string(comment.pop("severity"))
            if severity > severity_limit:
                logger.log.debug(f"Skipping {severity} comment: {comment}")
                continue

            if "start_line" not in comment:
                comment["start_line"] = comment["end_line"]

            adjusted_comment = code.diff.adjust_comment_to_best_hunk(
                review_request.hunks,
                comment,
            )
            if not adjusted_comment:
                logger.log.debug(f"No suitable hunk for comment: {comment}")
                continue
            else:
                comment = adjusted_comment

            # override path for determinism
            comment.update(path=review_request.path)

            if "end_line" in comment:
                if "start_line" in comment:
                    if int(comment["start_line"]) >= int(comment["end_line"]):
                        del comment["start_line"]

                comment.update(line=comment.pop("end_line"))

            if "end_side" in comment:
                comment.update(side=comment.pop("end_side"))

            logger.log.debug(f"File comment ({severity}): {comment}")
            comments.append(comment)

        logger.log.debug(f"Finished file review for `{review_request.path}`")

        return comments

    async def get_feedback(
            self,
            comments: list[model.Comment],
    ) -> model.Feedback:
        results = await single_tool_query(
            prompt_name="review-summary",
            tool_name="submit_review",
            model_name=self._model_name,
            builder=self._builder,
        )

        return model.Feedback(
            comments=comments,
            summary=results["summary"],
            overall_comment=results["feedback"],
            evaluation=results["event"],
        )
