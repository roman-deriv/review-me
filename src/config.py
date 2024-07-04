import json
import os


from model import AppConfig, GitHubConfig, LlmConfig


def from_env() -> AppConfig:
    debug = bool(os.environ.get("DEBUG", False))

    github_token = os.environ.get("GITHUB_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY")
    event_path = os.environ.get("GITHUB_EVENT_PATH")

    strategy = os.environ.get("LLM_STRATEGY", "anthropic")
    model = os.environ.get("MODEL")

    with open(event_path, "r") as f:
        event = json.load(f)

    pr_number = event["issue"]["number"]

    config = AppConfig(
        github=GitHubConfig(
            token=github_token,
            repository=repository,
            pr_number=pr_number,
        ),
        llm=LlmConfig(
            strategy=strategy,
            model=model,
        ),
        debug=debug,
    )

    return config
