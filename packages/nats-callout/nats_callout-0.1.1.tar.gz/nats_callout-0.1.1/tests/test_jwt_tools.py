import base64
import hashlib

import pytest
from nkeys import ErrInvalidSeed, PREFIX_BYTE_SERVER

from nats_callout.jwt_tools import (
    b64_decode_dict,
    b64_encode_dict,
    calculate_jti,
    decode_server_public_key,
)


class TestB64EncodeDict:
    """Tests for b64_encode_dict function."""

    def test_encode_simple_dict(self):
        """Test encoding a simple dictionary."""
        data = {"key": "value"}
        result = b64_encode_dict(data)

        # Should be a string
        assert isinstance(result, str)
        # Should not contain padding
        assert "=" not in result

    def test_encode_nested_dict(self):
        """Test encoding a nested dictionary."""
        data = {"outer": {"inner": "value"}, "list": [1, 2, 3]}
        result = b64_encode_dict(data)

        assert isinstance(result, str)
        assert "=" not in result

    def test_encode_empty_dict(self):
        """Test encoding an empty dictionary."""
        data = {}
        result = b64_encode_dict(data)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_encode_dict_with_various_types(self):
        """Test encoding dict with different value types."""
        data = {
            "string": "test",
            "int": 123,
            "float": 45.67,
            "bool": True,
            "none": None,
            "list": [1, 2, 3],
        }
        result = b64_encode_dict(data)

        assert isinstance(result, str)


class TestB64DecodeDict:
    """Tests for b64_decode_dict function."""

    def test_decode_simple_dict(self):
        """Test decoding a simple base64 string."""
        data = {"key": "value"}
        encoded = b64_encode_dict(data)
        decoded = b64_decode_dict(encoded)

        assert decoded == data

    def test_decode_nested_dict(self):
        """Test decoding a nested dictionary."""
        data = {"outer": {"inner": "value"}, "list": [1, 2, 3]}
        encoded = b64_encode_dict(data)
        decoded = b64_decode_dict(encoded)

        assert decoded == data

    def test_decode_empty_dict(self):
        """Test decoding an empty dictionary."""
        data = {}
        encoded = b64_encode_dict(data)
        decoded = b64_decode_dict(encoded)

        assert decoded == data


class TestB64RoundTrip:
    """Tests for round-trip encoding and decoding."""

    def test_roundtrip_preserves_data(self):
        """Test that encoding and decoding preserves data."""
        test_cases = [
            {"simple": "value"},
            {"nested": {"inner": {"deep": "value"}}},
            {"mixed": [1, "two", 3.0, None, True]},
            {"unicode": "こんにちは"},
            {"special": "!@#$%^&*()"},
        ]

        for data in test_cases:
            encoded = b64_encode_dict(data)
            decoded = b64_decode_dict(encoded)
            assert decoded == data


class TestCalculateJti:
    """Tests for calculate_jti function."""

    def test_calculate_jti_returns_string(self):
        """Test that JTI calculation returns a string."""
        claim = '{"test": "value"}'
        result = calculate_jti(claim)

        assert isinstance(result, str)

    def test_calculate_jti_no_padding(self):
        """Test that JTI has no base32 padding."""
        claim = '{"test": "value"}'
        result = calculate_jti(claim)

        # Base32 padding character
        assert "=" not in result

    def test_calculate_jti_deterministic(self):
        """Test that same input produces same JTI."""
        claim = '{"test": "value"}'
        result1 = calculate_jti(claim)
        result2 = calculate_jti(claim)

        assert result1 == result2

    def test_calculate_jti_different_for_different_input(self):
        """Test that different inputs produce different JTIs."""
        claim1 = '{"test": "value1"}'
        claim2 = '{"test": "value2"}'

        result1 = calculate_jti(claim1)
        result2 = calculate_jti(claim2)

        assert result1 != result2

    def test_calculate_jti_matches_sha256_base32(self):
        """Test that JTI matches expected SHA-256 + base32 encoding."""
        claim = '{"test": "value"}'
        result = calculate_jti(claim)

        # Manually calculate expected result
        sha256_hash = hashlib.sha256(claim.encode()).digest()
        expected = base64.b32encode(sha256_hash).decode().rstrip("=")

        assert result == expected

    def test_calculate_jti_empty_string(self):
        """Test JTI calculation with empty string."""
        claim = ""
        result = calculate_jti(claim)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_calculate_jti_unicode(self):
        """Test JTI calculation with unicode characters."""
        claim = '{"message": "こんにちは"}'
        result = calculate_jti(claim)

        assert isinstance(result, str)
        assert len(result) > 0


class TestDecodeServerPublicKey:
    """Tests for decode_server_public_key function."""

    def test_decode_valid_server_public_key(self):
        """Test decoding a valid server public key."""
        # This is a valid NATS server public key format
        # Format: base32 encoded with server prefix
        # Create a minimal valid server key
        raw_key = bytes([PREFIX_BYTE_SERVER, 0]) + b"\x00" * 30

        # Calculate CRC
        crc_bytes = self._calculate_crc(raw_key)
        key_with_crc = raw_key + crc_bytes

        # Encode as base32 without padding
        encoded = base64.b32encode(key_with_crc).decode().rstrip("=")

        prefix, result = decode_server_public_key(encoded.encode())

        assert isinstance(prefix, int)
        assert isinstance(result, bytes)
        assert len(result) >= 31  # At least 31 bytes (excluding first byte)

    def test_decode_server_key_with_padding(self):
        """Test that decoder handles keys with missing padding."""
        # Create a key that would need padding
        raw_key = bytes([PREFIX_BYTE_SERVER, 0]) + b"\x00" * 30
        crc_bytes = self._calculate_crc(raw_key)
        key_with_crc = raw_key + crc_bytes

        encoded = base64.b32encode(key_with_crc).decode().rstrip("=")
        # Remove some characters to test padding logic
        encoded_bytes = encoded.encode()

        prefix, result = decode_server_public_key(encoded_bytes)

        assert isinstance(result, bytes)

    def test_decode_invalid_base32_raises_error(self):
        """Test that invalid base32 raises ErrInvalidSeed."""
        invalid_key = b"!!!invalid-base32!!!"

        with pytest.raises(ErrInvalidSeed):
            decode_server_public_key(invalid_key)

    def test_decode_too_short_key_raises_error(self):
        """Test that too short key raises ErrInvalidSeed."""
        # Create key that's too short (less than 32 bytes when decoded)
        short_key = base64.b32encode(b"short").decode().rstrip("=")

        with pytest.raises(ErrInvalidSeed):
            decode_server_public_key(short_key.encode())

    def test_decode_wrong_prefix_raises_error(self):
        """Test that wrong prefix byte raises ErrInvalidSeed."""
        # Create key with wrong prefix (not server prefix)
        wrong_prefix_byte = 0xFF  # Not a valid server prefix
        raw_key = bytes([wrong_prefix_byte, 0]) + b"\x00" * 30
        crc_bytes = self._calculate_crc(raw_key)
        key_with_crc = raw_key + crc_bytes

        encoded = base64.b32encode(key_with_crc).decode().rstrip("=")

        with pytest.raises(ErrInvalidSeed):
            decode_server_public_key(encoded.encode())

    def _calculate_crc(self, data: bytes) -> bytes:
        """Helper to calculate CRC-16 for nkeys (simplified for testing)."""
        # For testing purposes, we'll use a simple 2-byte checksum
        # In production, nkeys uses a proper CRC-16
        checksum = sum(data) % 65536
        return checksum.to_bytes(2, byteorder="little")


class TestIntegration:
    """Integration tests for jwt_tools functions."""

    def test_jwt_claim_encoding_flow(self):
        """Test the flow of encoding JWT claims."""
        # Simulate a JWT claim
        claim_dict = {
            "iss": "test-issuer",
            "sub": "test-subject",
            "iat": 1234567890,
            "exp": 1234567890 + 3600,
        }

        # Encode the claim
        encoded = b64_encode_dict(claim_dict)

        # Calculate JTI
        claim_json = '{"iss":"test-issuer","sub":"test-subject","iat":1234567890,"exp":1234571490}'
        jti = calculate_jti(claim_json)

        # Decode and verify
        decoded = b64_decode_dict(encoded)

        assert decoded == claim_dict
        assert isinstance(jti, str)
        assert len(jti) > 0
