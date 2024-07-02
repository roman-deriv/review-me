import pathlib

import model

PROMPT_DIR = pathlib.Path(__file__).parent / "prompts"


def load(name, prefix: str = "system"):
    path = PROMPT_DIR / prefix / f"{name}.md"
    with open(path, "r") as file:
        return file.read()


class Builder:
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
        return self._preamble() + (
            f"Files Added: {self._context.added_files}\n"
            f"Files Deleted: {self._context.deleted_files}\n"
            f"Files Modified: {self._context.modified_files}\n"
            f"Changes:\n{combined_diff}"
        )

    def file_diff(self, filename: str) -> str:
        with open(filename, "r") as file:
            lines = file.readlines()

        content = "\n".join([f"{i} | {line}" for i, line in enumerate(lines, start=1)])

        return self._preamble() + (
            f"Original file: {filename}\n{content}\n\n"
            f"----------\n"
            f"Diff for file: {filename}\n{self._context.diffs[filename]}"
        )

    def review_summary(self, comments: list[dict[str, str]]):
        return self._preamble() + (
            f"Current Feedback:\n{comments}"
        )
