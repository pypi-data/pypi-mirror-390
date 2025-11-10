

import json
import redis
from functools import wraps

from tendril.config import REDIS_HOST
from tendril.config import REDIS_PORT
from tendril.config import REDIS_DB
from tendril.config import REDIS_PASSWORD

from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


redis_connection: redis.Redis = None


def _create_redis_connection():
    global redis_connection
    logger.info("Using Redis server at {}:{}:{} for caching"
                "".format(REDIS_HOST, REDIS_PORT, REDIS_DB))
    redis_connection = redis.Redis(host=REDIS_HOST,
                                   port=REDIS_PORT,
                                   db=REDIS_DB,
                                   password=REDIS_PASSWORD)


def cache(namespace=None, ttl=None, key=None, ser=json.dumps, deser=json.loads):
    if not redis_connection:
        _create_redis_connection()

    if not key:
        raise NotImplementedError(
            "Redis caching requires a key generator to be provided. "
            "The caching mechanism does not yet auto generate keys "
            "from functions arguments.")

    def _wrapper_factory(func):
        if not namespace:
            logger.warn("No caching namespace was provided for function {}. "
                        "Using 'generic_cache' instead.".format(func))

        @wraps(func)
        def wrapper_func(*args, **kwargs):
            cache_key = "{}:{}".format(namespace, key(*args, **kwargs))
            cached_value = redis_connection.get(cache_key)
            if cached_value:
                logger.debug("Cache Hit: {} {}".format(func, cache_key))
                return deser(cached_value)
            value = func(*args, **kwargs)
            logger.debug("Cache Miss: {} {}".format(func, cache_key))
            redis_connection.set(cache_key, ser(value), ex=ttl)
            return value

        return wrapper_func

    return _wrapper_factory
