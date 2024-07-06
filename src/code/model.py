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


class FileDiffModel(BaseModel):
    filename: str
    diff: str


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


class CommentBoundsModel(BaseModel):
    start_line: int
    start_side: Side | None = None
    end_line: int
    end_side: Side | None = None


class CommentModel(BaseModel):
    bounds: CommentBoundsModel
    body: str
    severity: Severity
