from core.ml_codec import encode_ml, decode_ml
from core.crypto.pin_crypto import encrypt_data, decrypt_data


class ProtectionError(Exception):
    """Raised when protection or reveal fails."""


def protect_data(data: bytes, pin: str) -> dict:
    """
    Full protection pipeline:
    Reversible ML Transform -> PIN-derived AES-256-GCM

    Args:
        data (bytes): raw file bytes (ANY type)
        pin (str): user PIN

    Returns:
        encrypted_payload (dict)
    """
    if not isinstance(data, (bytes, bytearray)) or not data:
        raise ProtectionError("INVALID_DATA")

    if not isinstance(pin, str) or not pin:
        raise ProtectionError("INVALID_PIN")

    try:
        # 1️⃣ ML reversible obfuscation (byte-safe)
        ml_encoded = encode_ml(data, pin.encode())
    except Exception as e:
        raise ProtectionError("ML_ENCODING_FAILED") from e

    try:
        # 2️⃣ PIN-based encryption (PBKDF2 + AES-GCM)
        encrypted_payload = encrypt_data(
            ml_encoded,
            pin
        )
    except Exception as e:
        raise ProtectionError("ENCRYPTION_FAILED") from e

    return encrypted_payload


def reveal_data(encrypted_payload: dict, pin: str) -> bytes:
    """
    Full reveal pipeline:
    PIN-derived AES-256-GCM Decrypt -> Reversible ML Decode

    Returns:
        original_data (bytes)
    """
    if not isinstance(encrypted_payload, dict):
        raise ProtectionError("INVALID_ENCRYPTED_PAYLOAD")

    if not isinstance(pin, str) or not pin:
        raise ProtectionError("INVALID_PIN")

    try:
        # 1️⃣ AES-GCM decryption
        ml_encoded = decrypt_data(
            encrypted_payload,
            pin
        )
    except Exception:
        # WRONG_PIN or tampered ciphertext
        raise ProtectionError("DECRYPTION_FAILED")

    try:
        # 2️⃣ Reverse ML transform (byte-perfect)
        original_data = decode_ml(
            ml_encoded,
            pin.encode()
        )
    except Exception as e:
        raise ProtectionError("ML_DECODING_FAILED") from e

    if not isinstance(original_data, (bytes, bytearray)):
        raise ProtectionError("CORRUPTED_OUTPUT")

    return original_data
