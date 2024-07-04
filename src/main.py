import asyncio
import sys
import traceback

import github

import ai.assistant
import ai.prompt
import config
from app import App, get_pr, build_context
import logger


def main():
    try:
        cfg = config.from_env()
        pr = get_pr(cfg.github)
    except github.GithubException as e:
        logger.log.critical(f"Couldn't retrieve pull request from Github: {e}")
        sys.exit(69)
    except Exception as e:
        logger.log.critical(f"Problem during initial setup: {e}")
        sys.exit(42)

    try:
        context = build_context(pr)
        builder = ai.prompt.Builder(context)
        assistant = ai.assistant.Assistant(cfg.llm.model, builder)

        app = App(pr, assistant, debug=cfg.debug)

        asyncio.run(app.run())
    except Exception as e:
        logger.log.error(f"Problem during run: {e}")
        try:
            pr.create_issue_comment(
                f"Sorry, couldn't review your code because\n"
                f"```{traceback.format_exc()}```"
            )
        except github.GithubException as e2:
            logger.log.error(f"Problem posting error comment: {e2}")
            sys.exit(69)


if __name__ == "__main__":
    main()
