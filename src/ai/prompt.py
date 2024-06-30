import pathlib

PROMPT_DIR = pathlib.Path(__file__).parent / "prompts"


def load(name):
    with open(PROMPT_DIR / f"{name}.md", "r") as file:
        return file.read()
