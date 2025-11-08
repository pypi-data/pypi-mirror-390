from rick.base import Di
from rick.mixin import Injectable
from rick.resource import CacheInterface, CacheNull


class DummyCache(CacheNull, Injectable):
    """
    Dummy Cache Wrapper
    """

    def __init__(self, di: Di):
        super().__init__(di)
