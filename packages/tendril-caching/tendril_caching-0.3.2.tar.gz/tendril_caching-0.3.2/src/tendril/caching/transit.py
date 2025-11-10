

import json
from decimal import Decimal

from tendril.config import TRANSIT_CACHING_PROVIDER
from tendril.config import PLATFORM_CACHING_PROVIDER

from tendril.utils import log
logger = log.get_logger(__name__)

if not TRANSIT_CACHING_PROVIDER:
    TRANSIT_CACHING_PROVIDER = PLATFORM_CACHING_PROVIDER

if TRANSIT_CACHING_PROVIDER == 'redis':
    logger.info("Using Redis for the transit cache.")
    import redis
    from tendril.config import REDIS_HOST
    from tendril.config import REDIS_PORT
    from tendril.config import REDIS_DB
    from tendril.config import REDIS_PASSWORD
else:
    logger.warning("A valid TRANSIT_CACHING_PROVIDER is not configured "
                   "and a fallback is not presently implemented. Anything that "
                   "touches the transit cache will likely cause catastrophic "
                   "failure.")


redis_connection: redis.Redis = None


def _create_redis_connection():
    global redis_connection
    logger.info("Using Redis server at {}:{}:{} for transit caching"
                "".format(REDIS_HOST, REDIS_PORT, REDIS_DB))
    redis_connection = redis.Redis(host=REDIS_HOST,
                                   port=REDIS_PORT,
                                   db=REDIS_DB,
                                   password=REDIS_PASSWORD)


def _common(namespace=None, key=None):
    if not redis_connection:
        _create_redis_connection()

    if not key:
        raise NotImplementedError(
            "Redis transit caching requires a literal "
            "key to be provided."
        )

    if not namespace:
        logger.warn(f"No transit caching namespace was provided for "
                    f"key {key}. Using 'transit' instead.")
        namespace = 'transit'

    cache_key = "{}:{}".format(namespace, key)
    return cache_key


def write(value=None, namespace=None, ttl=None, key=None, ser=json.dumps, get=False):
    cache_key = _common(namespace=namespace, key=key)
    logger.debug(f"Writing {value} to {cache_key}")
    return redis_connection.set(cache_key, ser(value), ex=ttl, get=get)


def read(namespace=None, key=None, deser=json.loads):
    cache_key = _common(namespace=namespace, key=key)
    cached_value = redis_connection.get(cache_key)
    logger.debug(f"Read {cached_value} from {cache_key}")
    if cached_value:
        try:
            if issubclass(deser, Decimal) and isinstance(cached_value, bytes):
                cached_value = cached_value.decode()
        except TypeError:
            pass
        return deser(cached_value)
    else:
        return None

def find_keys(namespace, pattern):
    result = []
    cursor = '0'
    cache_key = _common(namespace, pattern)
    logger.debug(f"Searching for keys with pattern {cache_key}")
    while cursor != 0:
        cursor, keys = redis_connection.scan(cursor=cursor, match=cache_key)
        result.extend(keys)
    return result

def delete(namespace=None, key=None):
    cache_key = _common(namespace=namespace, key=key)
    redis_connection.delete(cache_key)
