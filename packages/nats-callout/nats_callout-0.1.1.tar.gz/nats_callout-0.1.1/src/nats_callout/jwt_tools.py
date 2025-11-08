"""JWT encoding/decoding utilities for NATS Auth Callout.

This module provides helper functions for JWT operations including
base64 encoding/decoding, JTI calculation, and NKey public key decoding.
"""
import base64
import binascii
import hashlib
import json

from nkeys import PREFIX_BYTE_SERVER, ErrInvalidSeed


def b64_encode_dict(data: dict) -> str:
    """Encode a dictionary as a URL-safe base64 string for JWT.

    Args:
        data: Dictionary to encode

    Returns:
        URL-safe base64 encoded string without padding
    """
    json_str = json.dumps(data)
    b64_bytes = base64.urlsafe_b64encode(json_str.encode())
    return b64_bytes.rstrip(b"=").decode()


def b64_decode_dict(b64_str: str) -> dict:
    """Decode a URL-safe base64 string to a dictionary.

    Args:
        b64_str: URL-safe base64 encoded string

    Returns:
        Decoded dictionary
    """
    return json.loads(base64.urlsafe_b64decode(b64_str + "==").decode())


def calculate_jti(claim: str) -> str:
    """Calculate JWT ID (JTI) from claim data.

    Generates a JTI by computing the SHA-256 hash of the claim string
    and encoding it as base32 without padding.

    Args:
        claim: JSON string representation of JWT claims

    Returns:
        Base32-encoded SHA-256 hash without padding
    """
    sha256_hash = hashlib.sha256(claim.encode()).digest()

    encoded = base64.b32encode(sha256_hash).decode()
    return encoded.rstrip("=")


def decode_server_public_key(src):  # noqa ANN001 B904 PLR2004
    """Decode a NATS server public key from NKey format.

    Decodes a base32-encoded NKey server public key and extracts the
    raw Ed25519 public key bytes. Validates the key prefix to ensure
    it's a server key.

    Args:
        src: Base32-encoded NKey server public key (bytes)

    Returns:
        Tuple of (prefix, raw_public_key) where raw_public_key is
        the Ed25519 public key bytes

    Raises:
        ErrInvalidSeed: If the key is malformed or not a server key
    """
    # Add missing padding if required.
    padding = bytearray()
    padding += b"=" * (-len(src) % 8)

    try:
        base32_decoded = base64.b32decode(src + padding)
        raw = base32_decoded[: (len(base32_decoded) - 2)]
    except binascii.Error as exc:
        raise ErrInvalidSeed from exc

    if len(raw) < 32:
        raise ErrInvalidSeed

    # 248 = 11111000
    b1 = raw[0] & 248

    # 7 = 00000111
    b2 = (raw[0] & 7) << 5 | ((raw[1] & 248) >> 3)

    if b1 != PREFIX_BYTE_SERVER:
        raise ErrInvalidSeed

    prefix = b2
    result = raw[1 : (len(raw))]
    return prefix, result
