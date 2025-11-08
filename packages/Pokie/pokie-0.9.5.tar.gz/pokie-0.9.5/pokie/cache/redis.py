import pickle

from rick.base import Di
from rick.mixin import Injectable
from rick.resource.redis import RedisCache as BaseRedisCache

from pokie.constants import DI_REDIS


class RedisCache(BaseRedisCache, Injectable):
    def __init__(self, di: Di):
        if not di.has(DI_REDIS):
            raise RuntimeError("DI_REDIS not found; maybe RedisFactory is missing?")
        self.set_di(di)
        super().__init__(backend=di.get(DI_REDIS))
