import structlog
from contextlib import contextmanager
import structlog.contextvars
import logging
import sys


def configure_logger():
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.PATHNAME,
            ]
        ),
    ]

    structlog_processors = shared_processors + [
        structlog.processors.dict_tracebacks,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure(
        processors=structlog_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


@contextmanager
def bound_context(**kwargs):
    with structlog.contextvars.bound_contextvars(**kwargs):
        yield


class ProjectStructLogger:
    def __init__(self, logger):
        self.logger = logger

    def debug(self, project_id: str, user_id: str, message: str):
        with bound_context(project_id=str(project_id), user_id=str(user_id)):
            self.logger.debug(message)

    def info(self, project_id: str, user_id: str, message: str):
        with bound_context(project_id=str(project_id), user_id=str(user_id)):
            self.logger.info(message)

    def warning(self, project_id: str, user_id: str, message: str):
        with bound_context(project_id=str(project_id), user_id=str(user_id)):
            self.logger.warning(message)

    def error(
        self, project_id: str, user_id: str, message: str, exc_info: bool = False
    ):
        with bound_context(project_id=str(project_id), user_id=str(user_id)):
            self.logger.error(message, exc_info=exc_info)
