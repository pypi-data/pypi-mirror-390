import functools
import logging
from contextvars import ContextVar
from typing import Self, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.db.database import sessionmanager

from ..db.models.log import Log

request_log: ContextVar[list] = ContextVar("request_log")
db_log: ContextVar[list] = ContextVar("db_log")


T = TypeVar("T")


def log(func):  # noqa
    """Log decorator for synchronous functions.

    See alog for more information.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):  # noqa
        if logger.isEnabledFor(logging.DEBUG):
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            logger.debug(f"function {func.__name__} called with args {signature}")

        return func(*args, **kwargs)

    return wrapper


def alog(func):  # noqa
    """Log decorator for fastapi routes and asynchronous functions.

    Since we are using return await func, this only works for async functions
    inspect.isawaitable returns False on the decorated functions, so we cannot
    make it usable for both worlds.

    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):  # noqa
        if logger.isEnabledFor(logging.DEBUG):
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            logger.debug(f"function {func.__name__} called with args {signature}")

        return await func(*args, **kwargs)

    return wrapper


class InMemoryContextHandler(logging.Handler):
    def emit(self: Self, record: logging.LogRecord) -> None:
        request_log.get([]).append(self.format(record))


class InMemoryDBLogContextHandler(logging.Handler):
    def emit(self: Self, record: logging.LogRecord) -> None:
        if hasattr(record, "dbmodel"):
            dbmodel_class = getattr(record, "dbmodel")
            instance = dbmodel_class(
                title=self.format(record),
                **record.__dict__,
            )
            db_log.get([]).append(instance)


def print_request_log() -> None:
    print(*request_log.get([]), sep="\n")


async def save_db_log(db: AsyncSession) -> None:
    """Save the log entries stored in the ContextVar to the database.

    Args:
        db (AsyncSession): The database session.

    """
    db.add_all(db_log.get([]))
    await db.flush()


def reset_request_log() -> None:
    request_log.set([])


def reset_db_log() -> None:
    """Reset the db log entries stored in the ContextVar."""
    db_log.set([])


# Set up the logger
logger = logging.getLogger("mmisp")
in_memory_handler = InMemoryContextHandler()
in_memory_db_log_handler = InMemoryDBLogContextHandler()
log_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
dblog_formatter = logging.Formatter("%(message)s")
in_memory_handler.setFormatter(log_formatter)
in_memory_db_log_handler.setFormatter(dblog_formatter)
logger.addHandler(in_memory_handler)
logger.addHandler(in_memory_db_log_handler)

# adapter


sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.addHandler(in_memory_handler)


def get_jobs_logger(name: str, debug: bool = False) -> logging.LoggerAdapter:
    """
    Returns a logger which is intended to be used for jobs.

    Args:
        name: The name of the job.

    Returns:
        logging.LoggerAdapter: The logger for the job.

    """
    logger = logging.LoggerAdapter(
        logger=logging.getLogger(f"mmisp.jobs.{name}"),
        extra=dict(
            dbmodel=Log,
            model=name,
            model_id=0,
            action="execute_job",
            user_id=0,
            email="SYSTEM",
            org="SYSTEM",
            description="",
            change="",
            ip="",
        ),
    )
    if debug:
        logger.setLevel(logging.DEBUG)
    return logger


def add_ajob_db_log(func):  # noqa
    """
    This decorator is used to add the logged entries to the database. This function is only for async functions.
    Only works in combination with the mmisp logger.
    """

    @functools.wraps(func)
    async def log_wrapper(*args, **kwargs):  # noqa
        reset_request_log()
        reset_db_log()
        try:
            res = await func(*args, **kwargs)
            async with sessionmanager.session() as db:
                await save_db_log(db)
        except:
            print("Exception occured")
            raise
        finally:
            print_request_log()

        return res

    return log_wrapper


def add_job_db_log(func):  # noqa
    """
    This decorator is used to add the logged entries to the database.
    This function is only for synchronous functions.
    But the returned function is async because the database session is async.
    Only works in combination with the mmisp logger.

    """

    @functools.wraps(func)
    async def log_wrapper(*args, **kwargs):  # noqa
        reset_request_log()
        reset_db_log()
        try:
            res = func(*args, **kwargs)
            async with sessionmanager.session() as db:
                await save_db_log(db)
        except:
            print("Exception occured")
            raise
        finally:
            print_request_log()

        return res

    # Maybe add asyncio.run(log_wrapper(*args, **kwargs)) instead
    # of log_wrapper(*args, **kwargs) in the return statement
    return log_wrapper
