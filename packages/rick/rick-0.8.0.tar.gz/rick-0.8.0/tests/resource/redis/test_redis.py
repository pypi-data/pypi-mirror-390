from time import sleep

from rick.base import ShallowContainer


class TestRedisCache:
    def test_get_set_remove(self, redis_client):
        key = "shallow:cfg"
        test_data = {"foo": "bar", "baz": 123}
        obj = ShallowContainer(test_data)
        assert redis_client.has(key) is False
        redis_client.set(key, obj)
        assert redis_client.has(key) is True

        record = redis_client.get(key)
        assert record is not None
        assert isinstance(record, ShallowContainer)
        assert list(record.asdict().keys()) == list(test_data.keys())

        assert redis_client.remove(key) is True
        assert redis_client.has(key) is False
        assert redis_client.remove(key) is False
        assert redis_client.has(key) is False

    def test_ttl(self, redis_client):
        key = "shallow:cfg"
        test_data = {"foo": "bar", "ttl": "test"}
        obj = ShallowContainer(test_data)
        assert redis_client.has(key) is False
        redis_client.set(key, obj, ttl=1)
        assert redis_client.has(key) is True
        sleep(2)
        assert redis_client.has(key) is False

    def test_purge(self, redis_client):
        key = "shallow:cfg"
        test_data = {"foo": "bar", "purge": "test"}
        obj = ShallowContainer(test_data)
        assert redis_client.has(key) is False
        redis_client.set(key, obj)
        assert redis_client.has(key) is True
        redis_client.purge()
        assert redis_client.has(key) is False
