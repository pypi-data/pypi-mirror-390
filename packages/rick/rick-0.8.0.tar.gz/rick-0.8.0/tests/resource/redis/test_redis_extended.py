"""
Extended test suite for RedisCache

Tests cover:
- Custom serializers (JSON, MessagePack)
- Prefix functionality
- Hit/miss rate tracking
- Backend wrapping
- Edge cases and error conditions
- Multiple data types
"""

import json
import pickle
from datetime import datetime
from decimal import Decimal

import pytest
from rick.base import ShallowContainer
from rick.resource.redis import RedisCache
from rick.serializer.msgpack import msgpack


class TestRedisCacheCustomSerializers:
    """Test RedisCache with custom serializers"""

    def test_json_serializer(self, redis_container):
        """Test using JSON serializer instead of pickle"""

        def json_serialize(obj):
            return json.dumps(obj).encode("utf-8")

        def json_deserialize(data):
            return json.loads(data.decode("utf-8"))

        cache = RedisCache(
            host=redis_container.get_container_host_ip(),
            port=redis_container.get_exposed_port(6379),
            db=0,
            serializer=json_serialize,
            deserializer=json_deserialize,
        )

        try:
            key = "json:test"
            data = {"name": "John", "age": 30, "active": True}

            cache.set(key, data)
            result = cache.get(key)

            assert result == data
            assert result["name"] == "John"
            assert result["age"] == 30
            assert result["active"] is True
        finally:
            cache.purge()
            cache.close()

    def test_msgpack_serializer(self, redis_container):
        """Test using MessagePack serializer for complex types"""
        cache = RedisCache(
            host=redis_container.get_container_host_ip(),
            port=redis_container.get_exposed_port(6379),
            db=0,
            serializer=msgpack.packb,
            deserializer=msgpack.unpackb,
        )

        try:
            key = "msgpack:complex"
            data = {
                "timestamp": datetime(2025, 1, 1, 12, 0, 0),
                "amount": Decimal("123.45"),
                "user": "alice",
                "count": 42,
            }

            cache.set(key, data)
            result = cache.get(key)

            assert result["user"] == "alice"
            assert result["count"] == 42
            assert result["amount"] == Decimal("123.45")
            assert result["timestamp"] == datetime(2025, 1, 1, 12, 0, 0)
            assert isinstance(result["timestamp"], datetime)
            assert isinstance(result["amount"], Decimal)
        finally:
            cache.purge()
            cache.close()

    def test_default_pickle_serializer(self, redis_client):
        """Test that default pickle serializer works with complex objects"""
        key = "pickle:shallow"
        obj = ShallowContainer({"nested": {"data": "value"}, "number": 123})

        redis_client.set(key, obj)
        result = redis_client.get(key)

        assert isinstance(result, ShallowContainer)
        assert result["number"] == 123
        assert result["nested"]["data"] == "value"


class TestRedisCachePrefix:
    """Test prefix functionality"""

    def test_prefix_isolation(self, redis_container):
        """Test that different prefixes isolate data"""
        cache1 = RedisCache(
            host=redis_container.get_container_host_ip(),
            port=redis_container.get_exposed_port(6379),
            db=0,
            prefix="app1:",
        )

        cache2 = RedisCache(
            host=redis_container.get_container_host_ip(),
            port=redis_container.get_exposed_port(6379),
            db=0,
            prefix="app2:",
        )

        try:
            key = "config"

            # Set different values in each cache
            cache1.set(key, {"app": "app1"})
            cache2.set(key, {"app": "app2"})

            # Verify isolation
            assert cache1.get(key)["app"] == "app1"
            assert cache2.get(key)["app"] == "app2"

            # Verify keys don't exist in other namespace
            cache1.remove(key)
            assert cache1.has(key) is False
            assert cache2.has(key) is True  # Still exists in app2
        finally:
            cache1.purge()
            cache2.purge()
            cache1.close()
            cache2.close()

    def test_set_prefix_dynamically(self, redis_client):
        """Test changing prefix at runtime"""
        key = "data"

        # Set with no prefix
        redis_client.set(key, "value1")

        # Change prefix and set again
        redis_client.set_prefix("test:")
        redis_client.set(key, "value2")

        # Verify both exist
        assert redis_client.get(key) == "value2"

        redis_client.set_prefix("")
        assert redis_client.get(key) == "value1"

    def test_prefix_with_special_characters(self, redis_container):
        """Test prefix with various characters"""
        cache = RedisCache(
            host=redis_container.get_container_host_ip(),
            port=redis_container.get_exposed_port(6379),
            db=0,
            prefix="app:v1:cache:",
        )

        try:
            key = "user:123"
            cache.set(key, {"name": "Alice"})

            assert cache.has(key) is True
            assert cache.get(key)["name"] == "Alice"

            # Full key in Redis is "app:v1:cache:user:123"
            cache.remove(key)
            assert cache.has(key) is False
        finally:
            cache.purge()
            cache.close()


class TestRedisCacheHitRate:
    """Test hit/miss rate tracking"""

    def test_hit_rate_calculation(self, redis_client):
        """Test hit rate calculation with hits and misses"""
        # Initial hit rate should be 0
        assert redis_client.hit_rate() == 0

        # Set some data
        redis_client.set("key1", "value1")
        redis_client.set("key2", "value2")

        # Generate hits
        redis_client.get("key1")  # hit
        redis_client.get("key2")  # hit

        # Verify all hits
        assert redis_client.hits == 2
        assert redis_client.misses == 0
        assert redis_client.hit_rate() == 1.0

        # Generate misses
        redis_client.get("nonexistent1")  # miss
        redis_client.get("nonexistent2")  # miss

        # Verify hit rate
        assert redis_client.hits == 2
        assert redis_client.misses == 2
        assert redis_client.hit_rate() == 0.5

    def test_hit_miss_tracking(self, redis_client):
        """Test that hits and misses are tracked correctly"""
        key = "test:key"

        # Miss on non-existent key
        result = redis_client.get(key)
        assert result is None
        assert redis_client.misses == 1
        assert redis_client.hits == 0

        # Set and hit
        redis_client.set(key, "value")
        result = redis_client.get(key)
        assert result == "value"
        assert redis_client.hits == 1
        assert redis_client.misses == 1

        # Multiple hits
        redis_client.get(key)
        redis_client.get(key)
        assert redis_client.hits == 3
        assert redis_client.misses == 1

    def test_hit_rate_after_remove(self, redis_client):
        """Test hit rate tracking after key removal"""
        key = "test:key"

        redis_client.set(key, "value")
        redis_client.get(key)  # hit

        redis_client.remove(key)
        redis_client.get(key)  # miss after removal

        assert redis_client.hits == 1
        assert redis_client.misses == 1
        assert redis_client.hit_rate() == 0.5


class TestRedisCacheBackendWrapping:
    """Test wrapping existing Redis clients"""

    def test_wrap_existing_redis_client(self, redis_container):
        """Test wrapping a pre-existing Redis client"""
        import redis

        # Create a raw Redis client
        raw_client = redis.Redis(
            host=redis_container.get_container_host_ip(),
            port=redis_container.get_exposed_port(6379),
            db=0,
        )

        # Wrap it in RedisCache
        cache = RedisCache(backend=raw_client)

        try:
            key = "wrapped:key"
            data = {"wrapped": True}

            cache.set(key, data)
            assert cache.has(key) is True

            result = cache.get(key)
            assert result["wrapped"] is True

            # Verify we can access the underlying client
            assert cache.client() is raw_client
        finally:
            cache.purge()
            cache.close()

    def test_backend_with_prefix(self, redis_container):
        """Test backend wrapping with prefix"""
        import redis

        raw_client = redis.Redis(
            host=redis_container.get_container_host_ip(),
            port=redis_container.get_exposed_port(6379),
            db=0,
        )

        cache = RedisCache(backend=raw_client, prefix="wrapped:")

        try:
            cache.set("key", "value")
            assert cache.get("key") == "value"

            # Change prefix
            cache.set_prefix("other:")
            assert cache.get("key") is None  # Different namespace
        finally:
            cache.purge()
            cache.close()


class TestRedisCacheDataTypes:
    """Test various Python data types"""

    def test_none_value(self, redis_client):
        """Test storing and retrieving None"""
        key = "none:test"

        redis_client.set(key, None)
        result = redis_client.get(key)

        assert result is None

    def test_boolean_values(self, redis_client):
        """Test storing and retrieving booleans"""
        redis_client.set("bool:true", True)
        redis_client.set("bool:false", False)

        assert redis_client.get("bool:true") is True
        assert redis_client.get("bool:false") is False

    def test_numeric_types(self, redis_client):
        """Test various numeric types"""
        test_data = {
            "int": 42,
            "float": 3.14159,
            "negative": -100,
            "zero": 0,
            "large": 999999999999999999,
        }

        for key, value in test_data.items():
            redis_client.set(f"num:{key}", value)

        for key, expected in test_data.items():
            result = redis_client.get(f"num:{key}")
            assert result == expected
            assert type(result) == type(expected)

    def test_string_types(self, redis_client):
        """Test various string values"""
        test_strings = {
            "simple": "hello",
            "unicode": "こんにちは",
            "emoji": "🎉🚀",
            "multiline": "line1\nline2\nline3",
            "empty": "",
            "special": "special!@#$%^&*()_+-=[]{}|;:',.<>?/~`",
        }

        for key, value in test_strings.items():
            redis_client.set(f"str:{key}", value)

        for key, expected in test_strings.items():
            assert redis_client.get(f"str:{key}") == expected

    def test_list_values(self, redis_client):
        """Test storing and retrieving lists"""
        test_lists = {
            "simple": [1, 2, 3, 4, 5],
            "mixed": [1, "two", 3.0, True, None],
            "nested": [[1, 2], [3, 4], [5, 6]],
            "empty": [],
        }

        for key, value in test_lists.items():
            redis_client.set(f"list:{key}", value)

        for key, expected in test_lists.items():
            assert redis_client.get(f"list:{key}") == expected

    def test_dict_values(self, redis_client):
        """Test storing and retrieving dictionaries"""
        test_dicts = {
            "simple": {"a": 1, "b": 2},
            "nested": {"user": {"name": "Alice", "age": 30}},
            "mixed": {"str": "value", "int": 42, "bool": True, "list": [1, 2, 3]},
            "empty": {},
        }

        for key, value in test_dicts.items():
            redis_client.set(f"dict:{key}", value)

        for key, expected in test_dicts.items():
            assert redis_client.get(f"dict:{key}") == expected

    def test_set_values(self, redis_client):
        """Test storing and retrieving sets"""
        test_set = {1, 2, 3, 4, 5}

        redis_client.set("set:test", test_set)
        result = redis_client.get("set:test")

        assert isinstance(result, set)
        assert result == test_set

    def test_tuple_values(self, redis_client):
        """Test storing and retrieving tuples"""
        test_tuple = (1, 2, "three", 4.0)

        redis_client.set("tuple:test", test_tuple)
        result = redis_client.get("tuple:test")

        assert isinstance(result, tuple)
        assert result == test_tuple


class TestRedisCacheEdgeCases:
    """Test edge cases and error conditions"""

    def test_get_nonexistent_key(self, redis_client):
        """Test getting a key that doesn't exist"""
        result = redis_client.get("does:not:exist")
        assert result is None

    def test_remove_nonexistent_key(self, redis_client):
        """Test removing a key that doesn't exist"""
        result = redis_client.remove("does:not:exist")
        assert result is False

    def test_has_nonexistent_key(self, redis_client):
        """Test checking existence of non-existent key"""
        assert redis_client.has("does:not:exist") is False

    def test_overwrite_existing_key(self, redis_client):
        """Test overwriting an existing key"""
        key = "overwrite:test"

        redis_client.set(key, "value1")
        assert redis_client.get(key) == "value1"

        redis_client.set(key, "value2")
        assert redis_client.get(key) == "value2"

    def test_large_value(self, redis_client):
        """Test storing and retrieving large values"""
        # Create a large dictionary
        large_dict = {f"key_{i}": f"value_{i}" * 100 for i in range(1000)}

        redis_client.set("large:data", large_dict)
        result = redis_client.get("large:data")

        assert result == large_dict
        assert len(result) == 1000

    def test_very_long_key_name(self, redis_client):
        """Test using a very long key name"""
        long_key = "a" * 1000
        value = "test value"

        redis_client.set(long_key, value)
        assert redis_client.has(long_key) is True
        assert redis_client.get(long_key) == value

        redis_client.remove(long_key)
        assert redis_client.has(long_key) is False

    def test_special_characters_in_key(self, redis_client):
        """Test keys with special characters"""
        special_keys = [
            "key:with:colons",
            "key/with/slashes",
            "key-with-dashes",
            "key_with_underscores",
            "key.with.dots",
            "key@with@at",
        ]

        for key in special_keys:
            redis_client.set(key, f"value for {key}")

        for key in special_keys:
            assert redis_client.get(key) == f"value for {key}"

    def test_binary_data(self, redis_client):
        """Test storing binary data"""
        binary_data = b"\x00\x01\x02\x03\x04\x05"

        redis_client.set("binary:test", binary_data)
        result = redis_client.get("binary:test")

        assert result == binary_data
        assert isinstance(result, bytes)


class TestRedisCacheClient:
    """Test client access methods"""

    def test_client_access(self, redis_client):
        """Test accessing the underlying Redis client"""
        client = redis_client.client()

        assert client is not None
        # Verify it's a Redis client
        assert hasattr(client, "get")
        assert hasattr(client, "set")
        assert hasattr(client, "exists")

    def test_direct_redis_operations(self, redis_client):
        """Test using Redis client directly for raw operations"""
        client = redis_client.client()

        # Set a raw value using the client
        client.set("raw:key", b"raw value")

        # Verify it exists
        assert client.exists("raw:key") == 1

        # Get it back
        result = client.get("raw:key")
        assert result == b"raw value"

    def test_close_connection(self, redis_container):
        """Test closing the Redis connection"""
        cache = RedisCache(
            host=redis_container.get_container_host_ip(),
            port=redis_container.get_exposed_port(6379),
            db=0,
        )

        # Set some data
        cache.set("test:key", "value")
        assert cache.get("test:key") == "value"

        # Close the connection
        cache.close()

        # After close, _redis should be None
        assert cache._redis is None


class TestRedisCacheMultipleOperations:
    """Test sequences of operations"""

    def test_multiple_sets_and_gets(self, redis_client):
        """Test multiple set and get operations"""
        data = {f"key{i}": f"value{i}" for i in range(100)}

        # Set all keys
        for key, value in data.items():
            redis_client.set(key, value)

        # Verify all keys exist
        for key in data.keys():
            assert redis_client.has(key) is True

        # Get all values
        for key, expected_value in data.items():
            assert redis_client.get(key) == expected_value

        # Remove all keys
        for key in data.keys():
            assert redis_client.remove(key) is True

        # Verify all removed
        for key in data.keys():
            assert redis_client.has(key) is False

    def test_set_get_remove_cycle(self, redis_client):
        """Test repeated set/get/remove cycles"""
        key = "cycle:key"

        for i in range(10):
            # Set
            redis_client.set(key, f"value{i}")
            assert redis_client.has(key) is True

            # Get
            assert redis_client.get(key) == f"value{i}"

            # Remove
            assert redis_client.remove(key) is True
            assert redis_client.has(key) is False

    def test_update_existing_values(self, redis_client):
        """Test updating existing values multiple times"""
        key = "update:key"

        for i in range(100):
            redis_client.set(key, i)

        # Final value should be 99
        assert redis_client.get(key) == 99


class TestRedisCacheShallowContainer:
    """Test specific ShallowContainer integration"""

    def test_shallow_container_roundtrip(self, redis_client):
        """Test storing and retrieving ShallowContainer objects"""
        key = "container:test"
        data = {"name": "Alice", "age": 30, "active": True}
        container = ShallowContainer(data)

        redis_client.set(key, container)
        result = redis_client.get(key)

        assert isinstance(result, ShallowContainer)
        assert result["name"] == "Alice"
        assert result["age"] == 30
        assert result["active"] is True

    def test_nested_shallow_container(self, redis_client):
        """Test nested ShallowContainer objects"""
        key = "container:nested"
        data = {
            "user": {"name": "Bob", "email": "bob@example.com"},
            "settings": {"theme": "dark", "notifications": True},
        }
        container = ShallowContainer(data)

        redis_client.set(key, container)
        result = redis_client.get(key)

        assert isinstance(result, ShallowContainer)
        assert result["user"]["name"] == "Bob"
        assert result["settings"]["theme"] == "dark"

    def test_shallow_container_with_prefix(self, redis_container):
        """Test ShallowContainer with key prefix"""
        cache = RedisCache(
            host=redis_container.get_container_host_ip(),
            port=redis_container.get_exposed_port(6379),
            db=0,
            prefix="containers:",
        )

        try:
            key = "config"
            container = ShallowContainer({"db": "postgres", "port": 5432})

            cache.set(key, container)
            result = cache.get(key)

            assert isinstance(result, ShallowContainer)
            assert result["db"] == "postgres"
        finally:
            cache.purge()
            cache.close()
