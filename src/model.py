import dataclasses

type Filename = str
type FileDiff = str
type CommitMessage = str
type CommentBody = str
type Comment = dict[str, str]


@dataclasses.dataclass
class GitHubConfig:
    token: str
    repository: str
    pr_number: int


@dataclasses.dataclass
class LlmConfig:
    strategy: str
    model: str


@dataclasses.dataclass
class AppConfig:
    github: GitHubConfig
    llm: LlmConfig
    debug: bool = False


@dataclasses.dataclass
class FileReviewRequest:
    path: str
    changes: str
    related_changed: str
    reason: str

@dataclasses.dataclass
class ReviewContext:
    title: str
    description: str
    commit_messages: list[CommitMessage]
    issue_comments: list[CommentBody]
    review_comments: list[CommentBody]
    diffs: dict[Filename, FileDiff]
    added_files: list[Filename]
    modified_files: list[Filename]
    deleted_files: list[Filename]


@dataclasses.dataclass
class Feedback:
    summary: str
    comments: list[Comment]
    overall_comment: CommentBody
    evaluation: str
