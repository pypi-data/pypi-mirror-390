import logging
import sys
from pathlib import Path
from typing import TextIO

from databricks.labs.blueprint.logger import install_logger, NiceFormatter


def install_loggers(
    *,
    level: int | str = logging.DEBUG,
    stream: TextIO = sys.stderr,
    root: logging.Logger = logging.getLogger(),
    # TODO: This default is wrong, and is the (root?) cause for why we're logging into the source tree.
    logfile: Path = Path(__file__).parent / "lsp-server.log",
) -> None:
    """Install loggers for the application.

    Logs will be written to both stderr and the provided file.
    """
    # Note: blueprint clears all handlers, making this idempotent.
    install_logger(level, stream=stream, root=root)

    file_handler = logging.FileHandler(logfile, mode="w", encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(NiceFormatter(probe_tty=True, stream=file_handler.stream))
    root.addHandler(file_handler)
