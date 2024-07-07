import enum

from pydantic import BaseModel

from ai.schema import Side


class Severity(enum.IntEnum):
    CRITICAL = 0
    MAJOR = 1
    OPTIONAL = 2
    MINOR = 3
    NO_CHANGE = 4

    @classmethod
    def from_string(cls, s):
        return cls[s.upper()]


class GitHubCommentModel(BaseModel):
    path: str
    body: str
    line: int | None = None
    start_line: int | None = None
    side: Side | None = None
    start_side: Side | None = None


class HunkModel(BaseModel):
    start_line: int
    end_line: int
    changed_lines: set[int]

    def contains(self, line: int) -> bool:
        return self.start_line <= line <= self.end_line

    def is_changed_line(self, line: int) -> bool:
        return line in self.changed_lines

    def nearest_change(self, line: int) -> int:
        return min(self.changed_lines, key=lambda x: abs(x - line))

    def overlap(self, comment: GitHubCommentModel):
        overlap_start = max(comment.start_line, self.start_line)
        overlap_end = min(comment.line, self.end_line)
        return max(0, overlap_end - overlap_start + 1)

    def distance(self, comment: GitHubCommentModel) -> float:
        if comment.line < self.start_line:
            # Comment is before hunk
            return self.start_line - comment.line
        elif comment.start_line > self.end_line:
            # Comment is after hunk
            return comment.start_line - self.end_line
        elif (
                self.start_line <= comment.line <= self.end_line or
                self.start_line <= comment.start_line <= self.end_line
        ):
            # Comment overlaps hunk (negative distance)
            return -self.overlap(comment)

        return float("inf")


class FilePatchModel(BaseModel):
    filename: str
    diff: str
    hunks: list[HunkModel]


class CommentBoundsModel(BaseModel):
    start_line: int
    start_side: Side | None = None
    end_line: int
    end_side: Side | None = None


class CommentModel(BaseModel):
    filename: str
    bounds: CommentBoundsModel
    body: str
    severity: Severity
