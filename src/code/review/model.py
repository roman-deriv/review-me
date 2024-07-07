import enum

from pydantic import BaseModel

from ..model import FilePatchModel, GitHubCommentModel


class PullRequestContextModel(BaseModel):
    title: str
    description: str
    commit_messages: list[str]
    issue_comments: list[str]
    review_comments: list[str]
    patches: dict[str, FilePatchModel]
    added_files: list[str]
    modified_files: list[str]
    deleted_files: list[str]


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
    summary: str
    comments: list[GitHubCommentModel]
    overall_comment: str
    evaluation: str
