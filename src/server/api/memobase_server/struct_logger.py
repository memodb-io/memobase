import structlog
from contextlib import contextmanager
import structlog.contextvars

def configure_logger(enable_json_logs: bool = True):
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.CallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.PATHNAME,
                ]
            ),
            structlog.processors.dict_tracebacks,
            structlog.dev.ConsoleRenderer() if not enable_json_logs else structlog.processors.JSONRenderer(),
        ]
)

configure_logger()

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
