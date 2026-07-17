import logging
import sys
from pathlib import Path
import colorama

colorama.init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: colorama.Fore.CYAN,
        logging.INFO: colorama.Fore.GREEN,
        logging.WARNING: colorama.Fore.YELLOW,
        logging.ERROR: colorama.Fore.RED,
        logging.CRITICAL: colorama.Fore.RED + colorama.Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        reset = colorama.Style.RESET_ALL if color else ""
        # Copy record to avoid mutating the original one which might be passed to file handler
        record_copy = logging.makeLogRecord(record.__dict__)
        record_copy.levelname = f"{color}{record_copy.levelname}{reset}"
        return super().format(record_copy)


def get_logger(
    name: str, log_file: Path | str | None = None, level: int = logging.INFO
) -> logging.Logger:
    """Create and return a configured logger with colored console output and optional file output."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if get_logger is called multiple times for the same name
    if logger.hasHandlers():
        logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        "%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    if log_file:
        file_path = Path(log_file) if isinstance(log_file, str) else log_file
        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def set_log_file(log_file: str | Path, name: str = "wvs", level: int = logging.INFO):
    """Adds a file handler to an existing logger."""
    logger = logging.getLogger(name)
    file_path = Path(log_file) if isinstance(log_file, str) else log_file
    file_handler = logging.FileHandler(file_path, encoding="utf-8")
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
