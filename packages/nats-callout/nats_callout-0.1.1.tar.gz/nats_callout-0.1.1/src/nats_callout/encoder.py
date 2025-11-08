"""JWT encoding and decoding with NKey signatures.

This module provides the encoder abstraction for JWT operations,
including encoding claims with NKey signatures and verifying
server signatures on auth requests.
"""
import base64
import json
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Final, TypeVar

import jwt
import nkeys
from adaptix import Retort
from nacl.signing import VerifyKey
from nkeys import ErrInvalidSeed

from .claims import AuthRequestClaims
from .exceptions import (
    InvalidServerPublicKeyError,
    ServerSignatureVerificationError,
)
from .jwt_tools import (
    b64_encode_dict,
    calculate_jti,
    decode_server_public_key,
)

T = TypeVar("T")


class BaseEncoder(ABC):
    """Abstract base encoder for JWT operations with NKey signatures.

    Provides JWT encoding with ed25519-nkey signatures and verification
    of server signatures on authorization requests.

    Attributes:
        JWT_HEADER: Standard JWT header for all tokens
        kp: NKey keypair for signing JWTs
        json_dumps: JSON serialization function
        json_loads: JSON deserialization function
    """

    JWT_HEADER: Final = {"alg": "ed25519-nkey", "typ": "JWT"}
    kp: nkeys.KeyPair
    json_dumps: Callable[[Any], str]
    json_loads: Callable[[str], Any]

    def encode(self, data: Any) -> str:
        """Encode data as a signed JWT.

        Generates JTI if not present, encodes claims, and signs with
        the NKey keypair.

        Args:
            data: Claims data to encode

        Returns:
            Signed JWT string in format: header.payload.signature
        """
        data = self._dump_data(data)
        if not data.get("jti"):
            data["jti"] = ""
            jti = calculate_jti(json.dumps(data))
            data["jti"] = jti

        header_b64 = b64_encode_dict(self.JWT_HEADER)
        payload_b64 = b64_encode_dict(data)
        signing_input = f"{header_b64}.{payload_b64}".encode()
        signature = self.kp.sign(signing_input)
        signature_b64 = (
            base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
        )
        return f"{header_b64}.{payload_b64}.{signature_b64}"

    def decode_auth_request(self, token: str) -> AuthRequestClaims:
        """Decode and verify an authorization request JWT.

        Decodes the JWT, validates the header, and verifies the server's
        signature using the server's public key from the issuer field.

        Args:
            token: JWT token string

        Returns:
            Decoded and verified AuthRequestClaims

        Raises:
            ValueError: If JWT header is invalid
            InvalidServerPublicKeyError: If server public key is malformed
            ServerSignatureVerificationError: If signature verification fails
        """
        token_data = jwt.decode_complete(
            token,
            options={"verify_signature": False},
        )  # verify claims
        header_json = token_data["header"]
        if header_json != self.JWT_HEADER:
            raise ValueError("Invalid JWT header")
        payload_json = self.json_loads(token_data["payload"])

        # verify signature
        header_b64, payload_b64, signature_b64 = token.split(".")
        data = self._load_data(payload_json, AuthRequestClaims)
        iss = data.iss
        if iss is None:
            raise InvalidServerPublicKeyError
        try:
            _, raw_public = decode_server_public_key(iss.encode())
        except ErrInvalidSeed as exc:
            raise InvalidServerPublicKeyError from exc
        key = VerifyKey(raw_public)
        signing_input = f"{header_b64}.{payload_b64}".encode()
        signature = base64.urlsafe_b64decode(signature_b64 + "==")
        try:
            key.verify(signing_input, signature)
        except Exception as exc:
            raise ServerSignatureVerificationError from exc
        return data

    @abstractmethod
    def _load_data(self, data: dict, cls: type[T]) -> T:
        """Load dictionary data into a typed dataclass.

        Args:
            data: Dictionary to deserialize
            cls: Target dataclass type

        Returns:
            Instance of cls with data loaded
        """

    @abstractmethod
    def _dump_data(self, data: T) -> dict:
        """Dump dataclass instance to dictionary.

        Args:
            data: Dataclass instance to serialize

        Returns:
            Dictionary representation
        """


class AdaptixEncoder(BaseEncoder):
    """JWT encoder using Adaptix for dataclass serialization.

    Default encoder implementation that uses Adaptix library for
    converting between dataclasses and dictionaries.

    Args:
        retort: Optional custom Adaptix Retort instance for advanced
            serialization configuration
    """

    def __init__(
        self,
        retort: Retort | None = None,
    ):
        self._retort = retort or Retort()

    def _load_data(self, data: dict, cls: type[T]) -> T:
        """Load dictionary data using Adaptix.

        Args:
            data: Dictionary to deserialize
            cls: Target dataclass type

        Returns:
            Instance of cls with data loaded
        """
        return self._retort.load(data, cls)

    def _dump_data(self, data: Any) -> dict:
        """Dump dataclass instance using Adaptix.

        Args:
            data: Dataclass instance to serialize

        Returns:
            Dictionary representation
        """
        return self._retort.dump(data)
