import logging
import sys
from pathlib import Path

def setup_logger(name: str = "app") -> logging.Logger:
    """Configure and return a logger instance."""
    logger = logging.getLogger(name)

    if not logger.handlers:  # prevent duplicate handlers in reload
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)

        # File handler (append mode, creates directory if not exists)
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "app.log", mode="a")

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.setLevel(logging.INFO)  # default log level
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
