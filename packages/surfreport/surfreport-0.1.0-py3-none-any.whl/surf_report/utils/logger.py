import logging

# Constants
LOG_LEVEL = logging.DEBUG  # Default log level
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE = "surf_report.log"
LOG_FILE_MODE = "a"
LOG_TO_CONSOLE = False  # Change to `True` to enable console logging


def setup_logger(
    name: str = "surf_report",
    level: int = LOG_LEVEL,
    log_to_console: bool = LOG_TO_CONSOLE,
) -> logging.Logger:
    """
    Configures and returns a logger with optional console logging.

    Args:
        name (str): Name of the logger.
        level (int): Logging level.
        log_to_console (bool): Whether to enable console logging.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if not logger.hasHandlers():
        # File handler (logs to file)
        file_handler = logging.FileHandler(LOG_FILE, mode=LOG_FILE_MODE)
        file_handler.setFormatter(
            logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        )
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

        # Optional: Console handler (logs to terminal)
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(
                logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
            )
            console_handler.setLevel(level)
            logger.addHandler(console_handler)

    return logger


# Create a global logger instance with configurable console logging
logger = setup_logger(log_to_console=LOG_TO_CONSOLE)
