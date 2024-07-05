import re

import model


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
