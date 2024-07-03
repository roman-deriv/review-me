import config
import logging
from app import App


logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('review-me.log'), logging.StreamHandler()])

logger = logging.getLogger(__name__)


def main():
    logger.info("main start")
    cfg = config.from_env()
    app = App(cfg)
    app.run()
    logger.info("main finish")


if __name__ == "__main__":
    main()
