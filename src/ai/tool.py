import json
import pathlib
from typing import Any

TOOL_DIR = pathlib.Path(__file__).parent / "tools"


def load_tool(name: str) -> dict[str, Any]:
    path = TOOL_DIR / f"{name}.json"
    with open(path, "r") as file:
        return json.load(file)


def get_all_tools() -> dict[str, dict[str, Any]]:
    tools = {}
    for file in TOOL_DIR.glob("*.json"):
        tool_name = file.stem
        tools[tool_name] = load_tool(tool_name)
    return tools


TOOLS = get_all_tools()
