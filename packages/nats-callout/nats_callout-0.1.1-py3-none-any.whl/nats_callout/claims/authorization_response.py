"""Authorization response JWT claims.

This module defines the data structures for authentication responses
sent by the auth callout service back to the NATS server.
"""
from dataclasses import dataclass
from typing import Literal

from .base import BaseClaims, BaseNats


@dataclass(kw_only=True)
class AuthResponseData(BaseNats):
    """Authorization response data.

    Contains either a user JWT granting access or an error message
    denying access.

    Attributes:
        type: Always "authorization_response"
        jwt: User JWT granting access (None if auth failed)
        error: Error message if authentication failed (None if success)
        issuer_account: Account that issued the response
    """

    type: Literal["authorization_response"] = "authorization_response"
    jwt: str | None = None
    error: str | None = None
    issuer_account: str | None = None


@dataclass(kw_only=True)
class AuthResponseClaims(BaseClaims[AuthResponseData]):
    """Complete JWT claims for an authorization response.

    Combines standard JWT claims with AuthResponseData.
    """
