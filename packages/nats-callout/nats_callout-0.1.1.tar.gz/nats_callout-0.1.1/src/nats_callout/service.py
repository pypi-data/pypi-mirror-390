"""Base service for implementing NATS Auth Callout handlers.

This module provides the abstract base class for creating authentication
and authorization handlers that respond to NATS server auth requests.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from functools import cached_property

import nkeys

from .claims import (
    AuthRequestClaims,
    AuthRequestData,
    AuthResponseClaims,
    AuthResponseData,
    UserClaims,
    UserData,
)
from .encoder import BaseEncoder
from .exceptions import (
    AuthError,
    InvalidServerPublicKeyError,
    ServerSignatureVerificationError,
)


class BaseAuthCalloutService(ABC):
    """Abstract base class for NATS Auth Callout service handlers.

    Subclasses must implement the authentication logic and set required
    properties. The service handles JWT encoding/decoding, signature
    verification, and error handling automatically.

    Attributes:
        kp: NKey keypair for signing responses
        nkey_seed: NKey seed (string or bytes) for generating keypair
        encoder: JWT encoder instance (e.g., AdaptixEncoder)
        account: NATS account ID this service authorizes for

    Example:
        class MyAuthService(BaseAuthCalloutService):
            def __init__(self):
                self.encoder = AdaptixEncoder()
                self.nkey_seed = "SUABC..."
                self.account = "ACCOUNT_ID"

            async def _handle_auth_request_data(self, auth_request_data):
                # Validate credentials
                if valid:
                    return UserData(...)
                else:
                    raise AuthError("Invalid credentials")
    """

    kp: nkeys.KeyPair
    nkey_seed: str | bytes
    encoder: BaseEncoder
    account: str

    @abstractmethod
    async def _handle_auth_request_data(
        self,
        auth_request_data: AuthRequestData,
    ) -> UserData:
        """Handle authentication request and return user permissions.

        Implement this method to validate credentials and return user
        permissions. Raise AuthError if authentication fails.

        Args:
            auth_request_data: Authentication request containing client
                info, credentials, and connection options

        Returns:
            UserData with permissions for the authenticated user

        Raises:
            AuthError: If authentication fails (caught and returned as
                error response)
        """

    async def _handle(
        self,
        auth_request: AuthRequestClaims,
    ) -> AuthResponseClaims:
        """Process auth request and generate user JWT.

        Calls the subclass's _handle_auth_request_data method, creates
        a user JWT with 1-hour expiration, and wraps it in an auth
        response.

        Args:
            auth_request: Decoded authorization request claims

        Returns:
            Authorization response with user JWT

        Raises:
            AuthError: If authentication fails
        """
        account = self._get_account()
        now = datetime.now()
        iat = int(now.timestamp())
        auth_request_data = auth_request.nats
        user_data = await self._handle_auth_request_data(auth_request_data)
        user_claims = UserClaims(
            aud=account,
            sub=auth_request_data.user_nkey,
            iss=self._public_key,
            iat=iat,
            exp=iat + 3600,
            name=auth_request_data.user_nkey,
            nats=user_data,
        )
        user_jwt = self._encode_user_claims(user_claims)

        return AuthResponseClaims(
            iss=self._public_key,
            sub=auth_request.nats.user_nkey,
            aud=auth_request.nats.server_id.id,
            iat=iat,
            nats=AuthResponseData(
                jwt=user_jwt,
                type="authorization_response",
                version=auth_request.nats.version,
                tags=auth_request.nats.tags,
            ),
        )

    @cached_property
    def _nkey_seed(self) -> bytes:
        """Get NKey seed as bytes.

        Converts string seed to bytes if necessary.

        Returns:
            NKey seed as bytes
        """
        return (
            self.nkey_seed
            if isinstance(self.nkey_seed, bytes)
            else self.nkey_seed.encode()
        )

    def _get_account(self) -> str:
        """Get the NATS account ID.

        Returns:
            NATS account identifier
        """
        return self.account

    def _decode_auth_request(self, body: str) -> AuthRequestClaims:
        """Decode and verify authorization request JWT.

        Args:
            body: JWT string from NATS server

        Returns:
            Decoded and verified AuthRequestClaims

        Raises:
            AuthError: If signature or public key is invalid
        """
        try:
            return self.encoder.decode_auth_request(body)
        except ServerSignatureVerificationError as exc:
            raise AuthError("Invalid signature") from exc
        except InvalidServerPublicKeyError as exc:
            raise AuthError("Invalid server public key") from exc

    def _encode_auth_response(self, auth_response: AuthResponseClaims) -> str:
        """Encode authorization response as JWT.

        Args:
            auth_response: Authorization response claims

        Returns:
            Signed JWT string
        """
        return self.encoder.encode(auth_response)

    def _encode_user_claims(self, user_claims: UserClaims) -> str:
        """Encode user claims as JWT.

        Args:
            user_claims: User claims with permissions

        Returns:
            Signed JWT string
        """
        return self.encoder.encode(user_claims)

    @cached_property
    def _key_pair(self) -> nkeys.KeyPair:
        """Get NKey keypair from seed.

        Returns:
            NKey keypair for signing JWTs
        """
        nkey_seed = self._nkey_seed
        return nkeys.from_seed(nkey_seed)

    @cached_property
    def _public_key(self) -> str:
        """Get public key from NKey keypair.

        Returns:
            Public key string
        """
        kp = self._key_pair
        return kp.public_key.decode()

    async def _handle_raw(self, body: bytes | str) -> str:
        """Handle raw auth request and return JWT response.

        Main request handler that decodes the request, processes auth,
        and returns a response. Catches AuthError and returns error
        response instead of raising.

        Args:
            body: Raw JWT request from NATS (bytes or string)

        Returns:
            JWT response string (success or error)
        """
        if isinstance(body, bytes):
            body = body.decode()
        auth_request = self._decode_auth_request(body)
        now = datetime.now()
        iat = int(now.timestamp())
        try:
            auth_response = await self._handle(auth_request)
        except AuthError as e:
            auth_response = AuthResponseClaims(
                iss=self._public_key,
                sub=auth_request.nats.user_nkey,
                aud=auth_request.nats.server_id.id,
                iat=iat,
                nats=AuthResponseData(
                    jwt=None,
                    error=e.message,
                ),
            )

        return self._encode_auth_response(auth_response)

    async def __call__(self, body: bytes | str) -> str:
        """Handle auth request (callable interface).

        Allows the service instance to be called directly with a request.

        Args:
            body: Raw JWT request from NATS (bytes or string)

        Returns:
            JWT response string (success or error)
        """
        return await self._handle_raw(body)
