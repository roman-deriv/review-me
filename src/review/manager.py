from github.PullRequest import PullRequest

import model


def build_context(pull_request: PullRequest) -> model.ReviewContext:
    return model.ReviewContext(
        title=pull_request.title,
        description=pull_request.body,
        commit_messages=[
            commit.commit.message
            for commit in pull_request.get_commits()
        ],
        review_comments=[
            comment.body
            for comment in pull_request.get_review_comments()
        ],
        issue_comments=[
            comment.body
            for comment in pull_request.get_issue_comments()
        ],
        diffs={
            file.filename: file.patch
            for file in pull_request.get_files()
        }
    )


class ReviewManager:
    def __init__(self, context: model.ReviewContext):
        self._context = context

    def _preamble(self) -> str:
        return (
            f"PR Title: {self._context.title}\n\n"
            f"PR Body:\n{self._context.description}\n\n"
            f"PR Commits:\n- {"\n- ".join(self._context.commit_messages)}\n\n"
        )

    def overview(self) -> str:
        diffs = self._context.diffs
        combined_diff = "\n".join([
            f"Diff for file: {filename}\n{diff}"
            for filename, diff in diffs.items()
        ])
        return self._preamble() + f"Changes:\n{combined_diff}"

    def file_diff(self, filename: str) -> str:
        # TODO: add the entire file with line numbers
        return self._preamble() + (
            f"Diff for file: {filename}\n{self._context.diffs[filename]}"
        )

    def review_summary(self, comments: list[dict[str, str]]):
        return self._preamble() + (
            f"Current Feedback:\n{comments}"
        )
