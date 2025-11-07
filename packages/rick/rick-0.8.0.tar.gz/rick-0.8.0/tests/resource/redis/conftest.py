import pytest
from testcontainers.redis import RedisContainer
from rick.resource.redis import RedisCache, CryptRedisCache


@pytest.fixture(scope="module")
def redis_container():
    """Start a Redis container for the test module."""
    with RedisContainer("redis:7-alpine") as redis:
        yield redis


@pytest.fixture(scope="function")
def redis_client(redis_container):
    """Create a RedisCache client for each test."""
    cache = RedisCache(
        host=redis_container.get_container_host_ip(),
        port=redis_container.get_exposed_port(6379),
        db=0,
        decode_responses=False,
    )
    yield cache
    # Cleanup
    cache.purge()
    cache.close()


@pytest.fixture(scope="function")
def crypt_redis_client(redis_container):
    """Create a CryptRedisCache client for each test."""
    # 64 character test key
    test_key = "a" * 64
    cache = CryptRedisCache(
        key=test_key,
        host=redis_container.get_container_host_ip(),
        port=redis_container.get_exposed_port(6379),
        db=0,
        decode_responses=False,
    )
    yield cache
    # Cleanup
    cache.purge()
    cache.close()
