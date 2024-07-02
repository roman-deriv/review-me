import dataclasses

type Filename = str
type FileDiff = str
type CommitMessage = str
type Comment = str


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
class ReviewContext:
    title: str
    description: str
    commit_messages: list[CommitMessage]
    issue_comments: list[Comment]
    review_comments: list[Comment]
    diffs: dict[Filename, FileDiff]
    added_files: list[Filename]
    modified_files: list[Filename]
    deleted_files: list[Filename]


@dataclasses.dataclass
class Feedback:
    comments: list[dict[str, str]]
    overall_comment: Comment
    evaluation: str
