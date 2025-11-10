

import json
import uuid
import enum

from typing import Any
from typing import Optional
from pydantic import Field
from pydantic import UUID1
from tendril.utils.pydantic import TendrilTBaseModel
from fastapi.encoders import jsonable_encoder

from tendril.config import TOKENS_CACHING_PROVIDER
from tendril.config import PLATFORM_CACHING_PROVIDER
from tendril.authn.pydantic import UserReferenceTModel

from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)

if not TOKENS_CACHING_PROVIDER:
    TOKENS_CACHING_PROVIDER = PLATFORM_CACHING_PROVIDER

if TOKENS_CACHING_PROVIDER == 'redis':
    logger.info("Using Redis for the token cache.")
    import redis
    from tendril.config import REDIS_HOST
    from tendril.config import REDIS_PORT
    from tendril.config import REDIS_DB
    from tendril.config import REDIS_PASSWORD
    redis_connection: redis.Redis = None
else:
    logger.warning("A valid TOKENS_CACHING_PROVIDER is not configured "
                   "and a fallback is not presently implemented. Anything that "
                   "touches the tokens cache will likely cause catastrophic "
                   "failure.")
    redis_connection = None


class TokenStatus(enum.Enum):
    NEW = "NEW"
    INPROGRESS = "INPROGRESS"
    FAILED = "FAILED"
    CLOSED = "CLOSED"


class TokenProgressTModel(TendrilTBaseModel):
    done: int
    max: int


class GenericTokenTModel(TendrilTBaseModel):
    metadata: Any
    id: UUID1
    state: TokenStatus = Field(default=TokenStatus.NEW)
    user: Optional[UserReferenceTModel]
    current: Optional[str]
    error: Optional[dict[str, Any]]
    progress: Optional[TokenProgressTModel]


def _create_redis_connection():
    global redis_connection
    logger.info("Using Redis server at {}:{}:{} for token caching"
                "".format(REDIS_HOST, REDIS_PORT, REDIS_DB))
    redis_connection = redis.Redis(host=REDIS_HOST,
                                   port=REDIS_PORT,
                                   db=REDIS_DB,
                                   password=REDIS_PASSWORD)


def _cache_key(namespace=None, key=None):
    if not redis_connection:
        _create_redis_connection()

    if not namespace:
        logger.warn(f"No token caching namespace was provided for "
                    f"key {key}. Using 'ticket' instead.")
        namespace = 'ticket'

    cache_key = "{}:{}".format(namespace, key)
    return cache_key


def _write(cache_key, data, ex=None):
    return redis_connection.set(cache_key, data.json(), ex=ex)


def _read_raw(cache_key):
    return redis_connection.get(cache_key)


def _read(cache_key, tmodel=GenericTokenTModel):
    raw = _read_raw(cache_key)
    if not raw:
        return None
    return tmodel.parse_raw(raw)


def open(namespace, metadata, ttl=None, key=None, user=None,
         current=None, progress_max=None, tmodel=GenericTokenTModel):
    if not key:
        key = uuid.uuid1()
    cache_key = _cache_key(namespace=namespace, key=key)
    logger.info(f"Creating token {cache_key}")
    params = {
        'metadata': metadata,
        'id': key
    }
    if user:
        params['user'] = user
    if current:
        params['current'] = current
    if progress_max:
        progress = TokenProgressTModel(
            max=progress_max, done=0
        )
        params['progress'] = progress
    data = tmodel(**params)
    _write(cache_key, data, ex=ttl)
    return data


def read(namespace, key, tmodel=GenericTokenTModel):
    return _read(_cache_key(namespace=namespace, key=key),
                 tmodel=tmodel)


def update(namespace, key,
           state: TokenStatus = None,
           current: str = None,
           done: int = None, max: int = None,
           metadata=None, metadata_strategy='update',
           error: dict = None,
           ttl=None, tmodel=GenericTokenTModel):
    # TODO If no TTL provided, use the existing TTL
    cache_key = _cache_key(namespace, key)
    data: GenericTokenTModel = _read(cache_key, tmodel=tmodel)
    if state:
        data.state = state
    if current:
        data.current = current
    if done:
        data.progress.done = done
    if max:
        data.progress.max = max
    if error:
        data.error = error
    if metadata and metadata_strategy == 'update':
        data.metadata.update(metadata)
    return _write(cache_key, data, ex=ttl)


def close(namespace, key, failed=False, ttl=300,
          tmodel=GenericTokenTModel):
    if failed:
        state = TokenStatus.FAILED
    else:
        state = TokenStatus.CLOSED
    return update(namespace, key, state=state, ttl=ttl, tmodel=tmodel)


def delete(namespace=None, key=None):
    cache_key = _cache_key(namespace=namespace, key=key)
    redis_connection.delete(cache_key)
