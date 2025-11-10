

from tendril.utils.config import ConfigOption
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)

depends = ['tendril.config.core']


config_elements_caching = [
    ConfigOption(
        'PLATFORM_CACHING_PROVIDER',
        "None",
        "Platform Caching Provider. "
        "Currently supports 'redis' and 'local'"
    ),
    ConfigOption(
        'TRANSIT_CACHING_PROVIDER',
        "None",
        "Provider to use for Transit Caching. These are typically atomic pieces of "
        "meaningful but ephemeral information that must persist across disparate "
        "API requests."
    ),
    ConfigOption(
        'TOKENS_CACHING_PROVIDER',
        "None",
        "Provider to use for Token Caching. These are typically frequently written "
        "datastructures that live across a multi-step operation and are used to "
        "provide progress information. This is unrelated to auth tokens."
    )
]


config_elements_redis = [
    ConfigOption(
        'REDIS_HOST',
        "'localhost'",
        "Redis Host"
    ),
    ConfigOption(
        'REDIS_PORT',
        "6379",
        "Redis Port"
    ),
    ConfigOption(
        'REDIS_DB',
        "0",
        "Redis database to use"
    ),
    ConfigOption(
        'REDIS_PASSWORD',
        "None",
        "Redis Password",
        masked=True
    ),
]


def load(manager):
    logger.debug("Loading {0}".format(__name__))
    manager.load_elements(config_elements_caching,
                          doc="Caching Configuration")
    if manager.PLATFORM_CACHING_PROVIDER == "redis":
        manager.load_elements(config_elements_redis,
                              doc="Redis Configuration")
