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
    side: Side | None = None
    end_side: Side | None = None
    severity: Severity


class FileReviewResponseModel(BaseModel):
    feedback: list[CommentModel]


class ReviewResponseModel(BaseModel):
    feedback: list[CommentModel]
    summary: str
    event: str
