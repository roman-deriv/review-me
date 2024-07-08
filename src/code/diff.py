import re

import logger
from . import model


def parse_diff(patch: str) -> list[model.HunkModel]:
    hunks = []
    current_hunk = None
    current_line = 0

    for line in patch.split("\n"):
        if line.startswith("@@"):
            # Start of a new hunk
            match = re.search(r"@@ -\d+,\d+ \+(\d+),(\d+) @@", line)
            if match:
                if current_hunk:
                    hunks.append(current_hunk)
                start_line = int(match.group(1))
                line_count = int(match.group(2))
                end_line = start_line + line_count - 1
                current_hunk = model.HunkModel(
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


def closest_hunk(
    hunks: list[model.HunkModel],
    bounds: tuple[int, int],
) -> model.HunkModel | None:
    start_line, end_line = bounds
    best_hunk = None
    best_overlap = 0.0
    nearest_hunk = None
    min_distance = float("inf")

    for hunk in hunks:
        if not hunk.changed_lines:
            continue

        distance = hunk.distance(start_line, end_line)

        # Check for overlap with hunk
        if distance < 0:
            overlap = -distance
            if overlap > best_overlap:
                best_overlap = overlap
                best_hunk = hunk
                continue

        if distance < min_distance:
            min_distance = distance
            nearest_hunk = hunk

    return best_hunk or nearest_hunk


def adjust_comment_bounds_to_hunk(
    hunk: model.HunkModel,
    start_line: int,
    end_line: int,
) -> tuple[int, int]:
    logger.log.debug(f"Comment start line: {start_line}")
    logger.log.debug(f"Comment end line: {end_line}")

    # Adjust comment to fit within the hunk while preserving its length
    # Shift the hunk to the first modified line in the hunk
    comment_length = end_line - start_line
    adjusted_start = max(start_line, min(hunk.changed_lines))
    adjusted_end = adjusted_start + comment_length

    logger.log.debug(f"Shifted start line: {adjusted_start}")
    logger.log.debug(f"Shifted end line: {adjusted_end}")

    if adjusted_end > hunk.end_line:
        adjusted_end = max(hunk.changed_lines)
        adjusted_start = adjusted_end - comment_length

    logger.log.debug(f"Adjusted start line: {adjusted_start}")
    logger.log.debug(f"Adjusted end line: {adjusted_end}")

    # Ensure start and end are within the hunk's added lines
    adjusted_start = hunk.nearest_change(adjusted_start)
    adjusted_end = hunk.nearest_change(adjusted_end)

    logger.log.debug(f"Final start line: {adjusted_start}")
    logger.log.debug(f"Final end line: {adjusted_end}")

    return adjusted_start, adjusted_end
