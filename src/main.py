import asyncio

import ai.assistant
import ai.prompt
import config
from app import App, get_pr, build_context


def main():
    cfg = config.from_env()
    pr = get_pr(cfg.github)

    context = build_context(pr)
    builder = ai.prompt.Builder(context)
    assistant = ai.assistant.Assistant(cfg.llm.model, builder)

    app = App(pr, assistant, debug=cfg.debug)

    asyncio.run(app.run())


if __name__ == "__main__":
    main()
