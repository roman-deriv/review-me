import re
from enum import IntEnum

import logger
import model
from . import prompt
from .anthropic import tool_completion
from .tool import get_all_tools


def parse_diff(patch: str) -> list[model.Hunk]:
    hunks = []
    current_hunk = None
    current_line = 0

    for line in patch.split('\n'):
        if line.startswith("@@"):
            # Start of a new hunk
            match = re.search(r"@@ -\d+,\d+ \+(\d+),(\d+) @@", line)
            if match:
                if current_hunk:
                    hunks.append(current_hunk)
                start_line = int(match.group(1))
                line_count = int(match.group(2))
                end_line = start_line + line_count - 1
                current_hunk = model.Hunk(
                    start_line=start_line,
                    end_line=end_line,
                    changed_lines=set(),
                )
                current_line = start_line
        elif current_hunk:
            if line.startswith("+"):
                # This is an added or modified line
                current_hunk.changed_lines.add(current_line)
                current_line += 1
            elif not line.startswith("-"):
                # This is an unchanged line
                current_line += 1

    # Add the last hunk
    if current_hunk:
        hunks.append(current_hunk)

    return hunks


def is_comment_in_hunk(comment: model.Comment, hunks: list[model.Hunk]) -> bool:
    return any([hunk.contains_comment(comment) for hunk in hunks])


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

    async def files_to_review(
            self,
            context: model.ReviewContext,
    ) -> list[model.FileReviewRequest]:
        system_prompt = prompt.load("overview")
        results = await tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.overview(),
            model=self._model_name,
            tools=[self._tools["review_files"]],
            tool_override="review_files",
        )
        files = [
            model.FileReviewRequest(
                path=req["filename"],
                changes=req["changes"],
                related_changed=req["related_changes"],
                reason=req["reason"],
                diff=context.diffs[req["filename"]],
            )
            for req in results["files"]
        ]
        logger.log.debug(f"Files to review: {files}")
        return files

    async def review_file(
            self,
            review_request: model.FileReviewRequest,
            severity_limit: int = Severity.OPTIONAL,
    ) -> list[model.Comment]:
        system_prompt = prompt.load("file-review")

        hunks = parse_diff(review_request.diff)
        with open(review_request.path, "r") as source_file:
            source_code = source_file.readlines()

        results = await tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.file_review(review_request, source_code),
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

            if not is_comment_in_hunk(comment, hunks):
                # Treat this as a file comment
                if "end_line" in comment:
                    del comment["end_line"]
                if "start_line" in comment:
                    del comment["start_line"]

                logger.log.debug(f"Comment does not belong to a hunk: {comment}")

            # override path for determinism
            comment.update(path=review_request.path)
            if "end_line" in comment:
                if "start_line" in comment:
                    if int(comment["start_line"]) >= int(comment["end_line"]):
                        del comment["start_line"]

                # replace `end_line` with `line`
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
        system_prompt = prompt.load("review-summary")
        response = await tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.review_summary(comments),
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
