import pathlib

PROMPT_DIR = pathlib.Path(__file__).parent / "prompts"


def load(name, prefix: str = "system"):
    path = PROMPT_DIR / prefix / f"{name}.md"
    with open(path, "r") as file:
        return file.read()
