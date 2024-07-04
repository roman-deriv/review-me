import pathlib

import jinja2

import model

import logs


PROMPT_DIR = pathlib.Path(__file__).parent / "prompts"


def load(name, prefix: str = "system"):
    logs.debug("Starting to load prompts")
    path = PROMPT_DIR / prefix / f"{name}.md"
    with open(path, "r") as file:
        read_file = file.read()
        logs.debug("Finished loading prompts")
        return read_file


class Builder:
    def __init__(self, context: model.ReviewContext):
        logs.debug("Starting to create prompt builder")
        self._context = context
        self._user_templates = jinja2.Environment(
            loader=jinja2.FileSystemLoader(PROMPT_DIR / 'user'),
        )
        logs.debug("Finished creating prompt builder")

    def overview(self) -> str:
        logs.debug("Starting to create overview")
        oview = self._user_templates.get_template('overview.md').render(
            context=self._context,
        )
        logs.debug("Finished creating overview")
        return oview

    def file_diff(self, filename: str, source_code: list[str]) -> str:
        logs.debug("Starting to create file diff")
        fdiff = self._user_templates.get_template('file_diff.md').render(
            context=self._context,
            filename=filename,
            file=source_code,
            diff=self._context.diffs[filename],
        )
        logs.debug("Finished creating file diff")
        return fdiff

    def review_summary(self, comments: list[model.Comment]) -> str:
        logs.debug("Starting to create review summary")
        rsummary = self._user_templates.get_template('review_summary.md').render(
            context=self._context,
            comments=comments,
        )
        logs.debug("Finished creating review summary")
        return rsummary
