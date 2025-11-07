import logging
from typing import Callable, TypeVar

import structlog

F = TypeVar('F', bound=Callable[..., object])


def setup_logging(
        level: str = "INFO",
        json_format: bool = False,
        enable_stdlib: bool = False,
        **kwargs: object
) -> None:
    """
    Настройка логирования.

    :param level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
    :param json_format: Использовать JSON формат
    :param enable_stdlib: Также настроить стандартное логирование
    :param kwargs: Дополнительные аргументы
    """
    _setup_structlog(level, json_format, enable_stdlib, **kwargs)


def _setup_structlog(
        level: str = "INFO",
        json_format: bool = False,
        enable_stdlib: bool = False,
        **kwargs: object
) -> None:
    """
    Настройка structlog для структурированного логирования.

    :param level: Уровень логирования
    :param json_format: Использовать JSON формат
    :param enable_stdlib: Настроить стандартное логирование
    :param kwargs: Дополнительные аргументы
    """
    level_num = getattr(logging, level.upper(), logging.INFO)

    timestamper = structlog.processors.TimeStamper(fmt="iso")

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
    ]

    if json_format:
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]
    else:
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=True)
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    if enable_stdlib:
        _setup_stdlib_logging(level, **kwargs)

    # Устанавливаем уровень для structlog
    logging.getLogger("geodrive").setLevel(level_num)


def _setup_stdlib_logging(level: str = "INFO", **kwargs: object) -> None:
    """
    Настройка стандартного логирования как fallback.

    :param level: Уровень логирования
    :param kwargs: Дополнительные аргументы
    """
    level_num = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger("geodrive")
    logger.setLevel(level_num)
    logger.addHandler(handler)
    logger.propagate = False


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """
    Получить логгер.

    :param name: Имя логгера. Если None, возвращает корневой логгер 'geodrive'
    :return: Настроенный структурированный логгер
    """
    if name is None:
        name = "geodrive"
    else:
        name = f"geodrive.{name}"

    return structlog.get_logger(name)