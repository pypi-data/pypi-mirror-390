from pathlib import Path
from logging import getLogger, FileHandler, NullHandler

from mgost.console import Console


def verbosity_to_level(verbosity: int) -> int:
    assert isinstance(verbosity, int)
    level = (4-verbosity)*10
    return max(min(level, 51), 10)


def init_logging(verbosity: int, logs_folder: Path | None = None):
    assert isinstance(verbosity, int)
    level = verbosity_to_level(verbosity)
    Console.level = level
    logger = getLogger(__name__.split('.', 1)[0])
    logger.setLevel(level)
    if logs_folder:
        change_log_folder(logs_folder)
    else:
        logger.handlers = [NullHandler()]


def change_log_folder(logs_folder: Path) -> None:
    logger = getLogger(__name__.split('.', 1)[0])
    if not logs_folder.exists():
        logs_folder.mkdir(parents=True)
    logs_folder /= 'latest.log'
    handler = FileHandler(
        filename=logs_folder,
        encoding='utf-8'
    )
    logger.handlers = [handler]
