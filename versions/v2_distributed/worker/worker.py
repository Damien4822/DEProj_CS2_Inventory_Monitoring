from worker.consumer import start_consumer
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

# File name with current date
LOG_DIR = "/logs"
today_str = datetime.now().strftime("%Y-%m-%d")
log_file_path = os.path.join(LOG_DIR, f"worker_{today_str}.log")

# TimedRotatingFileHandler will automatically rotate at midnight
file_handler = TimedRotatingFileHandler(
    filename=log_file_path,
    when="midnight",  # rotate at midnight
    interval=1,
    backupCount=7,  # keep last 7 days
    encoding="utf-8"
)

# Format the logs
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler.setFormatter(formatter)

# Set up root logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
def main():
    logger.info("CS2 worker started")
    start_consumer(logger)

if __name__ == "__main__":
    main()