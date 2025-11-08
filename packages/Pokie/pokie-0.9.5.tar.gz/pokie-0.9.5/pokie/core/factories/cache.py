from rick.base import Di
from rick.resource.redis import RedisCache

from pokie.constants import DI_CACHE


def CacheFactory(_di: Di):
    """
    Cache factory
    Builds a CacheInterface object
    Currently only supports REDIS
    :param _di:
    :return:
    """
    _di.add(DI_CACHE, RedisCache)
