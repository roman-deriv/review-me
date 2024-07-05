import pathlib
import typing

import jinja2

import model

PROMPT_DIR = pathlib.Path(__file__).parent / "prompts"


class Builder:
    def __init__(self, context: model.ReviewContext):
        self._context = context
        self._templates = {
            "system": jinja2.Environment(
                loader=jinja2.FileSystemLoader(PROMPT_DIR / "system"),
            ),
            "user": jinja2.Environment(
                loader=jinja2.FileSystemLoader(PROMPT_DIR / "user"),
            )
        }

    def _load_template(
            self,
            name: str,
            prefix: typing.Literal["system", "user"] = "system",
    ) -> jinja2.Template:
        return self._templates[prefix].get_template(name)

    def render_template(self, name: str, **kwargs) -> str:
        template = self._load_template(f"{name}.md")
        overview = template.render(
            context=self._context,
            **kwargs
        )
        return overview
