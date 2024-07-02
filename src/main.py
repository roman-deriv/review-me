import config
from app import App


def main():
    cfg = config.from_env()
    app = App(cfg)
    app.run()


if __name__ == "__main__":
    main()
