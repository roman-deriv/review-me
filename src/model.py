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
    diff: str


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
class Hunk:
    start_line: int
    end_line: int
    changed_lines: set[int]

    def contains(self, line: int) -> bool:
        return self.start_line <= line <= self.end_line

    def is_changed_line(self, line: int) -> bool:
        return line in self.changed_lines

    def contains_comment(self, comment: Comment) -> bool:
        if "end_line" in comment:
            comment_line = int(comment["end_line"])
            if self.contains(comment_line):
                return self.is_changed_line(comment_line)
        elif "start_line" in comment and "end_line" in comment:
            comment_start = int(comment["start_line"])
            comment_end = int(comment["end_line"])

            is_comment_in_hunk = (
                    self.contains(comment_start) and
                    self.contains(comment_end)
            )

            if is_comment_in_hunk:
                return any(
                    line in self.changed_lines
                    for line in range(comment_start, comment_end + 1)
                )

        return False

    def nearest_line(self, line: int) -> int:
        return min(self.changed_lines, key=lambda x: abs(x - line))


@dataclasses.dataclass
class Feedback:
    summary: str
    comments: list[Comment]
    overall_comment: CommentBody
    evaluation: str
