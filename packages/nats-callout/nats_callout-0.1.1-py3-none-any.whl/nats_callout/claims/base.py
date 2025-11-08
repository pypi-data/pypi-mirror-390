"""Base classes for JWT claims structures.

This module defines the foundational dataclasses for all JWT claims
used in NATS authentication, including standard JWT fields and
NATS-specific claim data.
"""
from dataclasses import dataclass, field
from typing import Generic, Literal, TypeVar

T = TypeVar("T")


@dataclass(kw_only=True)
class BaseJwtClaims:
    """Standard JWT claim fields.

    Attributes:
        aud: Audience - who the JWT is intended for
        exp: Expiration time (Unix timestamp)
        jti: JWT ID - unique identifier for this token
        iat: Issued at time (Unix timestamp)
        iss: Issuer - who created and signed this JWT
        name: Human-readable name
        nbf: Not before time (Unix timestamp) - JWT not valid before this
        sub: Subject - who the JWT is about
    """

    aud: str | None = None
    exp: int | None = None
    jti: str | None = None
    iat: int | None = None
    iss: str | None = None
    name: str | None = None
    nbf: int | None = None
    sub: str | None = None


@dataclass(kw_only=True)
class BaseNats:
    """Base class for NATS-specific claim data.

    Attributes:
        type: Type of NATS claim (user, auth request, or auth response)
        version: NATS claim version (default: 2)
        tags: List of tags for categorization
    """

    type: Literal["user", "authorization_request", "authorization_response"]
    version: int = 2
    tags: list[str] = field(default_factory=list)


@dataclass(kw_only=True)
class BaseClaims(BaseJwtClaims, Generic[T]):
    """Generic JWT claims container with NATS-specific data.

    Combines standard JWT claims with NATS-specific claim data.

    Attributes:
        nats: NATS-specific claim data of type T
    """

    nats: T
