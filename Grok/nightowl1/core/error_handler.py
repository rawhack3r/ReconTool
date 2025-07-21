
import logging
import os
from datetime import datetime

class ErrorHandler:
    @staticmethod
    def setup_logging():
        os.makedirs("logs", exist_ok=True)
        logging.basicConfig(
            filename="logs/error.log",
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    @staticmethod
    def log_error(message):
        logging.error(message)

    @staticmethod
    def log_info(message):
        logging.info(message)

    @staticmethod
    def log_warning(message):
        logging.warning(message)

    @staticmethod
    def get_error_summary():
        try:
            with open("logs/error.log", "r") as f:
                return [line for line in f if "ERROR" in line]
        except:
            return []