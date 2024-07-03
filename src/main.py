import config
import logs
from app import App


def main():
    logs.info("main start")
    cfg = config.from_env()
    app = App(cfg)
    app.run()
    logs.info("main finish")


if __name__ == "__main__":
    main()
