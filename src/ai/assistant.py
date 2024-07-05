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


def adjust_comment_to_best_hunk(
        hunks: list[model.Hunk],
        comment: model.Comment,
) -> model.Comment | None:
    comment_start = comment["start_line"]
    comment_end = comment["end_line"]
    best_hunk = None
    best_overlap = 0
    nearest_hunk = None
    min_distance = float('inf')

    for hunk in hunks:
        if not hunk.changed_lines:
            continue

        # Check for overlap with hunk
        overlap_start = max(comment_start, hunk.start_line)
        overlap_end = min(comment_end, hunk.end_line)
        overlap = max(0, overlap_end - overlap_start + 1)

        if overlap > best_overlap:
            best_overlap = overlap
            best_hunk = hunk

        # Calculate distance if no overlap
        if comment_end < hunk.start_line:
            # Comment is before hunk
            distance = hunk.start_line - comment_end
            if distance < min_distance:
                min_distance = distance
                nearest_hunk = hunk
        elif comment_start > hunk.end_line:
            # Comment is after hunk
            distance = comment_start - hunk.end_line
            if distance < min_distance:
                min_distance = distance
                nearest_hunk = hunk

    if best_hunk:
        hunk = best_hunk
    elif nearest_hunk:
        hunk = nearest_hunk
    else:
        return None  # No suitable hunk found

    # Adjust comment to fit within the hunk while preserving its length
    comment_length = comment_end - comment_start
    adjusted_start = max(comment_start, hunk.start_line)
    adjusted_end = adjusted_start + comment_length

    if adjusted_end > hunk.end_line:
        adjusted_end = hunk.end_line
        adjusted_start = adjusted_end - comment_length

    # Ensure start and end are within the hunk's added lines
    adjusted_start = hunk.nearest_change(adjusted_start)
    adjusted_end = hunk.nearest_change(adjusted_end)

    comment["start_line"] = adjusted_start
    comment["end_line"] = adjusted_end
    return comment


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

            if "start_line" not in comment:
                comment["start_line"] = comment["end_line"]
            comment = adjust_comment_to_best_hunk(hunks, comment)

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
