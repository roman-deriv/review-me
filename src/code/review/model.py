from pydantic import BaseModel

from ..model import FileDiffModel, HunkModel


class PullRequestContext(BaseModel):
    title: str
    description: str
    commit_messages: list[str]
    issue_comments: list[str]
    review_comments: list[str]
    diffs: dict[str, FileDiffModel]
    added_files: list[str]
    modified_files: list[str]
    deleted_files: list[str]


class FileContext(BaseModel):
    path: str
    changes: str
    related_changes: str
    reason: str
    diff: FileDiffModel
    hunks: list[HunkModel]
