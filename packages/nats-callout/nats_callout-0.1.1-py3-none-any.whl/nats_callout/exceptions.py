"""Exceptions for NATS Auth Callout service."""


class AuthError(Exception):
    """Raised when authentication/authorization fails.

    This exception should be raised in authentication handlers to indicate
    that authentication failed. The service will catch this and return an
    error response to the NATS server.

    Args:
        message: Human-readable error message describing the auth failure
    """

    def __init__(self, message: str) -> None:
        self.message = message


class InvalidServerPublicKeyError(Exception):
    """Raised when the server public key in a JWT is invalid or malformed."""


class ServerSignatureVerificationError(Exception):
    """Raised when server signature verification fails on an auth request."""
