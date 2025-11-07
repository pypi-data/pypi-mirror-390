class CacheInterface:
    def get(self, key):
        pass

    def set(self, key, value, ttl=None):
        pass

    def has(self, key):
        pass

    def remove(self, key):
        pass

    def purge(self):
        pass

    def set_prefix(self, prefix):
        pass


class CacheNull(CacheInterface):
    def get(self, key):
        return None

    def set(self, key, value, ttl=None):
        return None

    def has(self, key):
        return False
