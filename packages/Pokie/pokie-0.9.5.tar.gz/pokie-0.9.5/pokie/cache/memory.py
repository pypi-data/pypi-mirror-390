import pickle

from rick.base import Di
from rick.mixin import Injectable
from rick.resource import CacheInterface

from pokie.contrib.auth.dto import UserRecord


class MemoryCache(CacheInterface, Injectable):
    """
    In-memory cache

    Note: This cache implementation is for unit testing purposes only; DO NOT use it for regular development or
     production!!!
    """

    def __init__(self, di: Di):
        super().__init__(di)
        self.cache = {}

    def get(self, key):
        if key not in self.cache.keys():
            return None
        return pickle.loads(self.cache.get(key))

    def set(self, key, value, ttl=None):
        self.cache[key] = pickle.dumps(value)

    def has(self, key):
        return key in self.cache.keys()

    def remove(self, key):
        if key in self.cache.keys():
            del self.cache[key]

    def purge(self):
        self.cache = {}
