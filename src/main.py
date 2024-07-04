import config
import logs
from app import App


def main():
    logs.info("Main is starting")
    cfg = config.from_env()
    app = App(cfg)
    app.run()
    logs.info("Main finished successfully")


if __name__ == "__main__":
    main()
