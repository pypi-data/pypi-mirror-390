import base64
import pickle

import redis

from rick.crypto import Fernet256
from rick.resource import CacheInterface


class RedisCache(CacheInterface):
    """
    Implements basic cache operations on a Redis backend

    Data is serialized using pickle. To access actual Redis-specific functions, the client is available via client()
    """

    def __init__(self, **kwargs):
        """
        :param kwargs: list of optional parameters

        Available parameters:
            host='localhost'
            port=6379,
            db=0
            password=None
            socket_timeout=None,
            socket_connect_timeout=None
            socket_keepalive=None
            socket_keepalive_options=None
            connection_pool=None
            unix_socket_path=None,
            encoding='utf-8'
            encoding_errors='strict'
            charset=None
            errors=None,
            decode_responses=False
            retry_on_timeout=False
            ssl=False
            ssl_keyfile=None
            ssl_certfile=None
            ssl_cert_reqs='required'
            ssl_ca_certs=None
            max_connections=None
            single_connection_client=False
            health_check_interval=0

            backend=None
            serializer=None
            deserializer=None
            prefix=None

        Note: if backend is specified, the value is used as redis adapter - this allows the wrapping of a pre-existing
        redis client instance into a RedisCache object:
        example:
            cache = RedisCache(backend=my_existing_redis)
        """

        # monitor stats on get()
        self.hits = 0
        self.misses = 0

        if "serializer" in kwargs:
            self._serialize = kwargs["serializer"]
            del kwargs["serializer"]
        else:
            self._serialize = pickle.dumps

        if "deserializer" in kwargs:
            self._deserialize = kwargs["deserializer"]
            del kwargs["deserializer"]
        else:
            self._deserialize = pickle.loads

        if "prefix" in kwargs:
            self._prefix = kwargs["prefix"]
            del kwargs["prefix"]
        else:
            self._prefix = ""

        if "backend" in kwargs:
            self._redis = kwargs["backend"]
        else:
            self._redis = redis.Redis(**kwargs)

    def get(self, key):
        v = self._redis.get(self._prefix + key)
        if v is None:
            self.misses += 1
            return None

        self.hits += 1
        return self._deserialize(v)

    def set(self, key, value, ttl=None):
        return self._redis.set(self._prefix + key, self._serialize(value), ex=ttl)

    def has(self, key):
        return self._redis.exists(self._prefix + key) == 1

    def remove(self, key):
        return self._redis.unlink(self._prefix + key) == 1

    def purge(self):
        return self._redis.flushdb()

    def client(self) -> redis.Redis:
        return self._redis

    def close(self):
        if hasattr(self, "_redis") and self._redis is not None:
            self._redis.close()
            self._redis = None

    def set_prefix(self, prefix):
        self._prefix = prefix

    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0

    def __del__(self):
        if hasattr(self, "_redis") and self._redis is not None:
            self._redis.close()
            self._redis = None


class CryptRedisCache(RedisCache):
    def __init__(self, key: str = None, **kwargs):
        """
        :param key_list: base64-encode key (256 bit)
        :param kwargs: list of optional parameters

        Available parameters:
            host='localhost'
            port=6379,
            db=0
            password=None
            socket_timeout=None,
            socket_connect_timeout=None
            socket_keepalive=None
            socket_keepalive_options=None
            connection_pool=None
            unix_socket_path=None,
            encoding='utf-8'
            encoding_errors='strict'
            charset=None
            errors=None,
            decode_responses=False
            retry_on_timeout=False
            ssl=False
            ssl_keyfile=None
            ssl_certfile=None
            ssl_cert_reqs='required'
            ssl_ca_certs=None
            max_connections=None
            single_connection_client=False
            health_check_interval=0
            backend=None
        """
        if key is None:
            raise ValueError("Empty fernet encryption key")

        if len(key) != 64:
            raise ValueError("CryptRedis: key must be a 64 byte string")
        key = base64.urlsafe_b64encode(key.encode("utf-8"))

        super().__init__(**kwargs)
        self._crypt = Fernet256(key)
        self._serialize = self._serializer
        self._deserialize = self._deserializer

    def _serializer(self, data):
        if data is not None:
            return self._crypt.encrypt(pickle.dumps(data))
        return data

    def _deserializer(self, data):
        if data is not None:
            return pickle.loads(self._crypt.decrypt(data))
        return data
