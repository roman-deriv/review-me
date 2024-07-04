import pathlib

import jinja2

import model
import logger


PROMPT_DIR = pathlib.Path(__file__).parent / "prompts"


def load(name, prefix: str = "system"):
    path = PROMPT_DIR / prefix / f"{name}.md"
    with open(path, "r") as file:
        read_file = file.read()
        return read_file


class Builder:
    def __init__(self, context: model.ReviewContext):
        self._context = context
        self._user_templates = jinja2.Environment(
            loader=jinja2.FileSystemLoader(PROMPT_DIR / 'user'),
        )

    def overview(self) -> str:
        overview = self._user_templates.get_template('overview.md').render(
            context=self._context,
        )
        logger.log.debug(f"Finished creating overview: {overview}")
        return overview

    def file_diff(self, file: model.FileReviewRequest, source_code: list[str]) -> str:
        fdiff = self._user_templates.get_template('file-diff.md').render(
            context=self._context,
            file=file,
            source_code=source_code,
        )
        logger.log.debug(f"Finished creating file diff: {fdiff}")
        return fdiff

    def review_summary(self, comments: list[model.Comment]) -> str:
        summary = self._user_templates.get_template('review-summary.md').render(
            context=self._context,
            comments=comments,
        )
        logger.log.debug(f"Finished creating review summary: {summary}")
        return summary
