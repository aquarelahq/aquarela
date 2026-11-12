import os
import time

_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_id() -> str:
    """A ULID: 48 bits of Unix milliseconds plus 80 random bits, Crockford base32."""
    value = (int(time.time() * 1000) << 80) | int.from_bytes(os.urandom(10))
    return "".join(_ALPHABET[(value >> shift) & 31] for shift in range(125, -1, -5))


def now_ms() -> int:
    return int(time.time() * 1000)
