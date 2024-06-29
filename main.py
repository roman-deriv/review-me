from app import config
from app.app import App


def main():
    cfg = config.from_env()
    app = App(cfg)
    app.run()


if __name__ == "__main__":
    main()