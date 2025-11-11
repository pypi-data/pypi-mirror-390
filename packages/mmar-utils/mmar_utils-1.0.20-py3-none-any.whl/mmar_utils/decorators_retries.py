import asyncio
import inspect
import time
from functools import wraps
from typing import Any, Callable, Tuple, Type, Union


Ex = Union[Type[BaseException], Tuple[Type[BaseException], ...]]
Func = Callable[..., Any]


class LoggerI:
    def warning(self, msg): ...


def retries(
    count: int | None = None,
    wait_seconds: int | list = 5,
    catch: Ex = Exception,
    nocatch: Ex = (),
    logger: Callable | None = None,
) -> Callable[[Func], Func]:
    """
    Decorator that retries a function (sync or async) if it raises exceptions.
    """
    if isinstance(wait_seconds, list):
        count = len(wait_seconds)
    else:
        count = count or 5
        wait_seconds = [wait_seconds] * count

    def should_retry(ex: Exception) -> bool:
        return isinstance(ex, catch) and not isinstance(ex, nocatch)

    def log_fail(attempt: int, func: Func, ex: Exception) -> None:
        if logger:
            logger(f"Failed attempt={attempt} to call {func.__name__} ( {type(ex).__name__}: {ex} )")

    def decorator(func: Func) -> Func:
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                for attempt, wait_s in zip(range(1, count + 1), wait_seconds):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as ex:
                        if not should_retry(ex) or attempt == count:
                            raise
                        log_fail(attempt, func, ex)
                        await asyncio.sleep(wait_s)

            return async_wrapper

        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                for attempt, wait_s in zip(range(1, count + 1), wait_seconds):
                    try:
                        return func(*args, **kwargs)
                    except Exception as ex:
                        if not should_retry(ex) or attempt == count:
                            raise
                        log_fail(attempt, func, ex)
                        time.sleep(wait_s)

            return sync_wrapper  # type: ignore

    return decorator
