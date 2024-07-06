from enum import IntEnum

import code.diff
import logger
import model
import review
from . import prompt
from .anthropic import tool_completion
from .tool import get_all_tools


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
        self._tools = get_all_tools()

    async def request_reviews(
            self,
            context: model.ReviewContext,
    ) -> list[model.FileReviewRequest]:
        system_prompt = self._builder.render_template(
            name="overview",
            prefix="system",
        )
        results = await tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.render_template(
                name="overview",
                prefix="user",
            ),
            model=self._model_name,
            tools=[self._tools["review_files"]],
            tool_override="review_files",
        )

        files = [
            review.parse_review_request(req, context)
            for req in results["files"]
        ]
        return files

    async def review_file(
            self,
            review_request: model.FileReviewRequest,
            severity_limit: int = Severity.OPTIONAL,
    ) -> list[model.Comment]:
        logger.log.debug(f"Reviewing file: {review_request.path}")

        system_prompt = self._builder.render_template(
            name="file-review",
            prefix="system",
        )

        logger.log.debug(f"Hunks: {review_request.hunks}")

        results = await tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.render_template(
                name="file-review",
                prefix="user",
                review_request=review_request,
            ),
            model=self._model_name,
            tools=[self._tools["post_feedback"]],
            tool_override="post_feedback",
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
                # replace `end_side` with `side`
                comment.update(side=comment.pop("end_side"))

            logger.log.debug(f"File comment ({severity}): {comment}")
            comments.append(comment)

        logger.log.debug(f"Finished file review for `{review_request.path}`")

        return comments

    async def get_feedback(
            self,
            comments: list[model.Comment],
    ) -> model.Feedback:
        system_prompt = self._builder.render_template(
            name="review-summary",
            prefix="system",
        )
        response = await tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.render_template(
                name="review-summary",
                prefix="user",
                comments=comments,
            ),
            model=self._model_name,
            tools=[self._tools["submit_review"]],
            tool_override="submit_review",
        )
        feedback = model.Feedback(
            comments=comments,
            summary=response["summary"],
            overall_comment=response["feedback"],
            evaluation=response["event"],
        )
        return feedback
