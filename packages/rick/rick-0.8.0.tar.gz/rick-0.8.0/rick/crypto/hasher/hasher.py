class HasherInterface:
    def hash(self, password: str) -> str:
        pass

    def is_valid(self, password: str, pw_hash: str) -> bool:
        pass

    def need_rehash(self, pw_hash, prefix=None):
        pass
