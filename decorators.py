import asyncio

from exceptions import TooManyTriesException
from loguru import logger


def tries(times: int, delay: float = 1.0):

    def func_wrapper(f):
        async def wrapper(*args, **kwargs):
            _times = times
            while _times:
                # noinspection PyBroadException
                try:
                    return await f(*args, **kwargs)
                except Exception as exc:
                    _times -= 1
                    if not _times:
                        raise TooManyTriesException() from exc
                    else:
                        logger.error(exc)
                        await asyncio.sleep(delay)
                        logger.warning("повторяем попытку")

        return wrapper

    return func_wrapper
