import logging


def get_logger(name: str = "bot", level: int = logging.INFO) -> logging.Logger:
    """Configure and return a logger."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    return logging.getLogger(name)
