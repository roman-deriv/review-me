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

    def _load_template(self, name: str) -> jinja2.Template:
        return self._user_templates.get_template(name)

    def render_template(self, name: str, **kwargs) -> str:
        template = self._load_template(f"{name}.md")
        overview = template.render(
            context=self._context,
            **kwargs
        )
        return overview
