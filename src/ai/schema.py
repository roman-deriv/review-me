import enum

from pydantic import BaseModel


class Severity(enum.StrEnum):
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    OPTIONAL = "OPTIONAL"
    MINOR = "MINOR"
    NO_CHANGE = "NO_CHANGE"


class Side(enum.StrEnum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class Event(enum.StrEnum):
    APPROVE = "APPROVE"
    COMMENT = "COMMENT"
    REQUEST_CHANGES = "REQUEST_CHANGES"


class FileReviewRequestModel(BaseModel):
    filename: str
    changes: str
    related_changes: str
    reason: str


class ReviewRequestsResponseModel(BaseModel):
    files: list[FileReviewRequestModel]


class CommentModel(BaseModel):
    path: str
    body: str
    start_line: int | None = None
    end_line: int
    start_side: Side | None = None
    end_side: Side | None = None
    severity: Severity

    def bounds(self) -> tuple[int, int]:
        if self.start_line:
            if self.start_line > self.end_line:
                return self.end_line, self.start_line
            else:
                return self.start_line, self.end_line
        else:
            return self.end_line, self.end_line


class FileReviewResponseModel(BaseModel):
    feedback: list[CommentModel]


class ReviewResponseModel(BaseModel):
    feedback: str
    summary: str
    event: Event
