import logging
from typing import Any, Literal

from rich.console import Console
from rich.logging import RichHandler

import user_agent_sdk


def get_logger(name: str) -> logging.Logger:
    if name.startswith("user_agent_sdk."):
        return logging.getLogger(name=name)

    return logging.getLogger(name=f"user_agent_sdk.{name}")


LogLevelType = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def configure_logging(
        level: LogLevelType | int = "INFO",
        logger: logging.Logger | None = None,
        enable_rich_tracebacks: bool | None = None,
        **rich_kwargs: Any,
) -> None:
    if logger is None:
        logger = logging.getLogger("user_agent_sdk")

    formatter = logging.Formatter("%(message)s")

    # Don't propagate to the root logger
    logger.propagate = False
    logger.setLevel(level)

    # Configure the handler for normal logs
    handler = RichHandler(
        console=Console(stderr=True),
        **rich_kwargs,
    )
    handler.setFormatter(formatter)

    # filter to exclude tracebacks
    handler.addFilter(lambda record: record.exc_info is None)

    # Configure the handler for tracebacks, for tracebacks we use a compressed format:
    # no path or level name to maximize width available for the traceback
    # suppress framework frames and limit the number of frames to 3

    import conductor

    traceback_handler = RichHandler(
        console=Console(stderr=True),
        show_path=False,
        show_level=False,
        rich_tracebacks=enable_rich_tracebacks,
        tracebacks_max_frames=3,
        tracebacks_suppress=[user_agent_sdk, conductor],
        **rich_kwargs,
    )
    traceback_handler.setFormatter(formatter)

    traceback_handler.addFilter(lambda record: record.exc_info is not None)

    # Remove any existing handlers to avoid duplicates on reconfiguration
    for hdlr in logger.handlers[:]:
        logger.removeHandler(hdlr)

    logger.addHandler(handler)
    logger.addHandler(traceback_handler)
