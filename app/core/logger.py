from app.core.config import LOGS_PATH
from datetime import datetime
import logging
import os


class LevelOnlyFilter(logging.Filter):
    """
    Restricts a handler to records of exactly one level, so debug/info/warning
    logs land only in their own file instead of cascading into each other.
    """
    def __init__(self, level: int):
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == self.level


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter with colors for better console readability.
    """
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
        'RESET': '\033[0m'
    }
    DIM = '\033[2m'
    BRIGHT = '\033[1m'

    def format(self, record):
        original_levelname = record.levelname

        if original_levelname in self.COLORS:
            colored_level = f"{self.COLORS[original_levelname]}{self.BRIGHT}{original_levelname:8s}{self.COLORS['RESET']}"
        else:
            colored_level = f"{original_levelname:8s}"

        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        colored_timestamp = f"{self.DIM}{timestamp}{self.COLORS['RESET']}"

        module_name = record.name
        if len(module_name) > 30:
            parts = module_name.split('.')
            if len(parts) > 3:
                module_name = '.'.join(parts[:2]) + '...' + '.'.join(parts[-2:])
        colored_module = f"{self.DIM}{module_name}{self.COLORS['RESET']}"

        formatted = f"{colored_timestamp} {colored_level} {colored_module} {record.getMessage()}"

        record.levelname = original_levelname
        return formatted


def get_logger(name: str = "app_logger") -> logging.Logger:
    """
    Stores daily logs, split by level, under logs/<date>/.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    date_dir = os.path.join(LOGS_PATH, today)
    os.makedirs(date_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not logger.handlers:
        file_formatter = logging.Formatter(
            "%(levelname)-8s | %(asctime)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        level_files = (
            (logging.DEBUG, "DEBUG.log", LevelOnlyFilter(logging.DEBUG)),
            (logging.INFO, "INFO.log", LevelOnlyFilter(logging.INFO)),
            (logging.WARNING, "WARNING.log", LevelOnlyFilter(logging.WARNING)),
            (logging.ERROR, "ERROR.log", None),
        )
        for level, filename, level_filter in level_files:
            file_handler = logging.FileHandler(os.path.join(date_dir, filename), encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(file_formatter)
            if level_filter is not None:
                file_handler.addFilter(level_filter)
            logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(ColoredFormatter())
        logger.addHandler(console_handler)

    return logger