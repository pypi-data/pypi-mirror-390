from pokie.cache import MemoryCache


class TestMemoryCache:

    def test_mutability(self, pokie_di):
        cache = MemoryCache(pokie_di)
        key = "key1"
        data = {"key": "value"}
        assert cache.has(key) is False
        cache.set(key, data)
        assert cache.has(key) is True
        # mutate stored object
        data["key"] = 3

        # test for cache immutability
        record = cache.get(key)
        assert record is not None
        assert record["key"] == "value"
