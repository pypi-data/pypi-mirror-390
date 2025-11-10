

from tendril.config import PLATFORM_CACHING_PROVIDER
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)

from .providers import dummy
no_cache = dummy.cache

if PLATFORM_CACHING_PROVIDER == 'redis':
    logger.info("Using Redis for the platform level cache.")
    from .providers import redis
    platform_cache = redis.cache
else:
    logger.info("Platform level cache not configured.")
    platform_cache = dummy.cache
