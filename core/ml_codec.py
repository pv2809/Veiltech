import numpy as np
import hashlib

CHUNK_SIZE = 256


def _get_permutation(key: bytes):
    """
    Generate a deterministic permutation from a key.
    """
    seed = int.from_bytes(hashlib.sha256(key).digest()[:4], "big")
    rng = np.random.default_rng(seed)
    perm = rng.permutation(CHUNK_SIZE)
    inv_perm = np.argsort(perm)
    return perm, inv_perm


def encode_ml(data: bytes, key: bytes) -> bytes:
    encoded = bytearray()
    perm, _ = _get_permutation(key)

    for i in range(0, len(data), CHUNK_SIZE):
        chunk = data[i:i + CHUNK_SIZE]
        if len(chunk) < CHUNK_SIZE:
            chunk += b"\x00" * (CHUNK_SIZE - len(chunk))

        scrambled = bytes(chunk[p] for p in perm)
        encoded.extend(scrambled)

    return bytes(encoded)


def decode_ml(encoded: bytes, key: bytes) -> bytes:
    decoded = bytearray()
    _, inv_perm = _get_permutation(key)

    for i in range(0, len(encoded), CHUNK_SIZE):
        chunk = encoded[i:i + CHUNK_SIZE]
        restored = bytes(chunk[p] for p in inv_perm)
        decoded.extend(restored)

    return bytes(decoded)
