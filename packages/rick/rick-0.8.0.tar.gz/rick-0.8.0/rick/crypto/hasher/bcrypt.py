import hashlib
import hmac

import bcrypt
from .hasher import HasherInterface


class BcryptHasher(HasherInterface):
    def __init__(self, rounds=None, prefix=None):
        if rounds is None:
            rounds = 12
        if prefix is None:
            prefix = "2b"
        self._rounds = rounds
        self._prefix = prefix

    def hash(self, password: str) -> str:
        """
        Hashes a password using bcrypt with random salt
        :param password: clear password to hash
        :return: hash string
        """
        if len(password) == 0:
            raise ValueError("hash(): empty password")

        password = hashlib.sha256(password.encode("utf-8")).hexdigest().encode("utf-8")
        salt = bcrypt.gensalt(rounds=self._rounds, prefix=self._prefix.encode("utf-8"))

        return bcrypt.hashpw(password, salt).decode("utf-8")

    def is_valid(self, password: str, pw_hash: str) -> bool:
        """
        Compares a cleartext password with a password hash
        :param password: clear password
        :param pw_hash: hash to validate
        :return: True if the hash matches the supplied password
        """
        pw_hash = pw_hash.encode("utf-8")
        password = hashlib.sha256(password.encode("utf-8")).hexdigest().encode("utf-8")

        return hmac.compare_digest(bcrypt.hashpw(password, pw_hash), pw_hash)

    def need_rehash(self, pw_hash, prefix=None):
        """
        Check if the number of rounds on the supplied hash is enough, or if one should re-hash the password
        :param pw_hash: hash to verify
        :param prefix: optional prefix
        :return: True if hash number of rounds is below current object configuration
        """
        if prefix is None:
            prefix = self._prefix
        if len(pw_hash) < 4:
            raise ValueError("hash(): hash cannot be empty")
        tokens = pw_hash[1:].split("$", 2)
        if len(tokens) < 3 or tokens[0] != prefix or not tokens[1].isdigit():
            raise ValueError("hash(): invalid hash")

        return int(tokens[1]) < self._rounds
