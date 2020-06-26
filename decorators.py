import asyncio
from functools import wraps
from loguru import logger


def retry(exceptions, tries=4, delay=3, backoff=2):
    """
    Retry calling the decorated function using an exponential backoff.

    Args:
        exceptions: The exception to check. may be a tuple of
            exceptions to check.
        tries: Number of times to try (not retry) before giving up.
        delay: Initial delay between retries in seconds.
        backoff: Backoff multiplier (e.g. value of 2 will double the delay
            each retry).
        logger: Logger to use. If None, print.
    """

    def deco_retry(f):

        @wraps(f)
        async def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return await f(*args, **kwargs)
                except exceptions as e:
                    msg = '{}, Retrying in {} seconds...'.format(e, mdelay)
                    logger.warning(msg)
                    await asyncio.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return await f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry
