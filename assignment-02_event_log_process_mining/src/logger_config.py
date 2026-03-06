import logging
import os
from datetime import datetime, timedelta

LOG_DIR = "logs"


def cleanup_old_logs(days=30):

    if not os.path.exists(LOG_DIR):
        return

    now = datetime.now()

    for file in os.listdir(LOG_DIR):

        path = os.path.join(LOG_DIR, file)

        if os.path.isfile(path):

            mtime = datetime.fromtimestamp(os.path.getmtime(path))

            if now - mtime > timedelta(days=days):
                os.remove(path)


def setup_logger():

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    cleanup_old_logs()

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")


    log_file = f"{LOG_DIR}/run_{run_id}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)

    return logger, run_id