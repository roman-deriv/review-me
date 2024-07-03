import asyncio

import config
from app import App


def main():
    cfg = config.from_env()
    app = App(cfg)

    asyncio.run(app.run())


if __name__ == "__main__":
    main()
