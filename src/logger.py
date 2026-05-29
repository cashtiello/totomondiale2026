"""
logger.py - Configurazione centralizzata del logging
"""
import logging
import sys
from pathlib import Path
from src.config import LOG_FILE, LOG_LEVEL, LOG_FORMAT, LOG_DATE, LOGS_DIR


def setup_logging() -> None:
    """Configura il sistema di logging su console e file."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE)

    root = logging.getLogger()
    root.setLevel(level)

    # Evita duplicati se chiamata più volte
    if root.handlers:
        return

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # File handler
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)   # sul file tutto
    fh.setFormatter(formatter)
    root.addHandler(fh)


def get_logger(name: str) -> logging.Logger:
    """Restituisce un logger con il nome specificato."""
    return logging.getLogger(name)
