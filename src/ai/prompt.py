import pathlib

import jinja2

import model

PROMPT_DIR = pathlib.Path(__file__).parent / "prompts"


def load(name, prefix: str = "system"):
    path = PROMPT_DIR / prefix / f"{name}.md"
    with open(path, "r") as file:
        return file.read()


class Builder:
    def __init__(self, context: model.ReviewContext):
        self._context = context
        self._user_templates = jinja2.Environment(
            loader=jinja2.FileSystemLoader(PROMPT_DIR / 'user'),
        )

    def overview(self) -> str:
        return self._user_templates.get_template('overview.md').render(
            context=self._context,
        )

    def file_diff(self, filename: str, source_code: list[str]) -> str:
        return self._user_templates.get_template('file_diff.md').render(
            context=self._context,
            filename=filename,
            file=source_code,
            diff=self._context.diffs[filename],
        )

    def review_summary(self, comments: list[model.Comment]) -> str:
        return self._user_templates.get_template('review_summary.md').render(
            context=self._context,
            comments=comments,
        )
