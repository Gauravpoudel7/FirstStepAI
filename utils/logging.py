"""Logging setup."""
import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s :: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    # Quiet down noisy libraries.
    for noisy in ("httpx", "chromadb", "sentence_transformers", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
