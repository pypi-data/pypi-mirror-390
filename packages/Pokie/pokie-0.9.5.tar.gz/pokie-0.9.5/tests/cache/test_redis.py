import pytest

from pokie.cache import MemoryCache, RedisCache
from pokie.constants import DI_REDIS

@pytest.fixture
def redis_cache(pokie_di):
    return RedisCache(pokie_di)


class TestRedisCache:

    def test_mutability(self, redis_cache):
        key = "key1"
        data = {"key": "value"}
        assert redis_cache.has(key) is False
        redis_cache.set(key, data)
        assert redis_cache.has(key) is True
        # mutate stored object
        data["key"] = 3

        # test for cache immutability
        record = redis_cache.get(key)
        assert record is not None
        assert record["key"] == "value"
