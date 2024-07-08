import enum

from pydantic import BaseModel


class Status(enum.StrEnum):
    ACCEPTABLE = "ACCEPTABLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNACCEPTABLE = "UNACCEPTABLE"


class Severity(enum.StrEnum):
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    OPTIONAL = "OPTIONAL"
    MINOR = "MINOR"
    NO_CHANGE = "NO_CHANGE"


class Side(enum.StrEnum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class Category(enum.StrEnum):
    FUNCTIONALITY = "FUNCTIONALITY"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    MAINTAINABILITY = "MAINTAINABILITY"
    READABILITY = "READABILITY"
    BEST_PRACTICES = "BEST_PRACTICES"


class Event(enum.StrEnum):
    APPROVE = "APPROVE"
    COMMENT = "COMMENT"
    REQUEST_CHANGES = "REQUEST_CHANGES"


class InitialAssessmentModel(BaseModel):
    status: Status
    summary: str


class ObservationTag(enum.StrEnum):
    DOCUMENTATION = "DOCUMENTATION"
    CODE_STYLE = "CODE_STYLE"
    TYPE_CHECKING = "TYPE_CHECKING"
    ERROR_HANDLING = "ERROR_HANDLING"


class ObservationModel(BaseModel):
    comment: str
    tag: ObservationTag


class FileReviewRequestModel(BaseModel):
    filename: str
    changes: str
    related_changes: str
    reason: str


class ReviewRequestsResponseModel(BaseModel):
    initial_assessment: InitialAssessmentModel
    observations: list[ObservationModel] | None = None
    files_for_review: list[FileReviewRequestModel] | None = None


class CommentModel(BaseModel):
    path: str
    body: str
    start_line: int | None = None
    end_line: int
    start_side: Side | None = None
    end_side: Side | None = None
    severity: Severity
    category: Category

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
    event: Event
    justification: str
