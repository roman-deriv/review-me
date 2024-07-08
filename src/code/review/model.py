import enum

from pydantic import BaseModel

from ..model import FilePatchModel, GitHubCommentModel


class FileContextModel(BaseModel):
    path: str
    changes: str
    related_changes: str
    reason: str
    patch: FilePatchModel


class Status(enum.IntEnum):
    ACCEPTABLE = 0
    REVIEW_REQUIRED = 1
    UNACCEPTABLE = 2


class InitialAssessmentModel(BaseModel):
    status: Status
    summary: str


class ObservationTag(enum.StrEnum):
    DOCUMENTATION = "documentation"
    CODE_STYLE = "code-style"
    TYPE_CHECKING = "type-checking"
    ERROR_HANDLING = "error-handling"


class ObservationModel(BaseModel):
    comment: str
    tag: ObservationTag


class OverviewModel(BaseModel):
    initial_assessment: InitialAssessmentModel
    observations: list[ObservationModel]
    file_contexts: list[FileContextModel]


class Feedback(BaseModel):
    comments: list[GitHubCommentModel]
    overall_comment: str
    evaluation: str
    justification: str
