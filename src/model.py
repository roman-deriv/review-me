import dataclasses
import typing

type Filename = str
type FileDiff = str
type CommitMessage = str
type CommentBody = str
type Comment = dict[str, typing.Any]


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
class Hunk:
    start_line: int
    end_line: int
    changed_lines: set[int]

    def contains(self, line: int) -> bool:
        return self.start_line <= line <= self.end_line

    def is_changed_line(self, line: int) -> bool:
        return line in self.changed_lines

    def nearest_change(self, line: int) -> int:
        return min(self.changed_lines, key=lambda x: abs(x - line))


@dataclasses.dataclass
class FileReviewRequest:
    path: str
    changes: str
    related_changed: str
    reason: str
    diff: str
    hunks: list[Hunk]


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
