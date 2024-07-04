import logging
import os


logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(os.environ.get("LOGFILE","default_logfile.log")), logging.StreamHandler()])

log = logging.getLogger(__name__)
