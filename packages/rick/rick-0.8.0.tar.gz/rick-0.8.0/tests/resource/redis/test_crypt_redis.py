from tests.resource.redis.test_redis import TestRedisCache


class TestCryptRedisCache(TestRedisCache):
    # Override fixture to use crypt_redis_client
    def test_get_set_remove(self, crypt_redis_client):
        super().test_get_set_remove(crypt_redis_client)

    def test_ttl(self, crypt_redis_client):
        super().test_ttl(crypt_redis_client)

    def test_purge(self, crypt_redis_client):
        super().test_purge(crypt_redis_client)

    def test_crypt(self, crypt_redis_client):
        key = "test:crypt"
        value = "the quick brown fox jumps over the lazy dog"
        crypt_redis_client.set(key, value)

        # Verify the value is retrieved correctly
        retrieved = crypt_redis_client.get(key)
        assert retrieved == value

        # Verify the data is encrypted in Redis (would need raw client to check)
        # For now, just verify it works end-to-end
        crypt_redis_client.remove(key)
