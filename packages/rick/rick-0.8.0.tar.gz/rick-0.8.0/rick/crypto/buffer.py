import hashlib
from io import BytesIO


def hash_buffer(method, buf: BytesIO) -> str:
    fn = getattr(hashlib, method)
    if not callable(fn):
        raise RuntimeError(
            "hash_buffer(): invalid hashing method:  '{}'".format(method)
        )
    buf.seek(0)
    return fn(buf.read()).hexdigest()


def sha256_hash(buf: BytesIO) -> str:
    buf.seek(0)
    return hashlib.sha256(buf.read()).hexdigest()


def sha1_hash(buf: BytesIO) -> str:
    buf.seek(0)
    return hashlib.sha1(buf.read()).hexdigest()


def sha512_hash(buf: BytesIO) -> str:
    buf.seek(0)
    return hashlib.sha512(buf.read()).hexdigest()


def blake2_hash(buf: BytesIO) -> str:
    buf.seek(0)
    return hashlib.blake2b(buf.read()).hexdigest()
