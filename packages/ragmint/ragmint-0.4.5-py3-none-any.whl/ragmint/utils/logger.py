import logging
from tqdm import tqdm


class Logger:
    """
    Centralized logger with optional tqdm integration and color formatting.
    """

    def __init__(self, name: str = "ragmint", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "\033[96m[%(asctime)s]\033[0m \033[93m%(levelname)s\033[0m: %(message)s",
                "%H:%M:%S",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def progress(self, iterable, desc="Processing", total=None):
        return tqdm(iterable, desc=desc, total=total)

def get_logger(name: str = "ragmint") -> Logger:
    return Logger(name)