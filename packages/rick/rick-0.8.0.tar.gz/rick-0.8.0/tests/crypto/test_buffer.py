import pytest
from io import BytesIO

from rick.crypto import sha256_hash, sha1_hash
from rick.crypto.buffer import blake2_hash, sha512_hash


@pytest.fixture
def buffer() -> BytesIO:
    return BytesIO(b"the quick brown fox jumps over the lazy dog")


class TestHashBuffer:
    def test_sha256(self, buffer):
        assert (
            sha256_hash(buffer)
            == "05c6e08f1d9fdafa03147fcb8f82f124c76d2f70e3d989dc8aadb5e7d7450bec"
        )

    def test_sha1(self, buffer):
        assert sha1_hash(buffer) == "16312751ef9307c3fd1afbcb993cdc80464ba0f1"

    def test_sha512(self, buffer):
        expected = (
            "801b90d850f51736249cb33df75e17918c2233d7a083cb9d27561160ae15f1e2c"
            "c2c97531fcdaa8426c654ba9c7c3a4b7d97ba770d09f0d839bff3047b2f5ce2"
        )
        assert sha512_hash(buffer) == expected

    def test_blake2(self, buffer):
        expected = (
            "b6d864419b922f8857e999f637f0e15449f2437b635e3a35c91799418f1e558d"
            "78b0c9071b6ddbf2794d24717046b597b2db114b81d6e79ee181bee9a9329c99"
        )
        assert blake2_hash(buffer) == expected
