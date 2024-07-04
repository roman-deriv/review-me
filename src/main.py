import asyncio
import traceback

import ai.assistant
import ai.prompt
import config
from app import App, get_pr, build_context
import logger


def main():


    try:
        cfg = config.from_env()
        pr = get_pr(cfg.github)
    except Exception as e:
        logger.log.debug(f"Problem during inital setup: {e}")
        exit(69)
    
    try:
        assert False
        context = build_context(pr)
        builder = ai.prompt.Builder(context)
        assistant = ai.assistant.Assistant(cfg.llm.model, builder)

        app = App(pr, assistant, debug=cfg.debug)

        asyncio.run(app.run())
    except Exception as e:
        logger.log.debug(f"Problem during run: {e}")
        pr.create_issue_comment(f"Sorry, couldn't review your code becasue\n```{traceback.format_exc()}```")
        exit(42)

    


if __name__ == "__main__":
    main()
