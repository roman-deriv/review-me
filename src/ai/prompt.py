import pathlib

import jinja2

import model


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
        return overview

    def file_review(
            self,
            review_request: model.FileReviewRequest,
            source_code: list[str],
    ) -> str:
        diff = self._user_templates.get_template('file-review.md').render(
            context=self._context,
            review_request=review_request,
            source_code=source_code,
        )
        return diff

    def review_summary(self, comments: list[model.Comment]) -> str:
        summary = self._user_templates.get_template('review-summary.md').render(
            context=self._context,
            comments=comments,
        )
        return summary
