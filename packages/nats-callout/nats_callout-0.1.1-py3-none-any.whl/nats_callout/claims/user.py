"""User JWT claims and permission structures.

This module defines the data structures for user JWTs that specify
what operations a user is authorized to perform on NATS.
"""
from dataclasses import dataclass, field
from typing import Literal

from .base import BaseClaims, BaseNats


@dataclass(kw_only=True)
class PubSubPermissions:
    """Pub/Sub permissions with allow/deny subject lists.

    Attributes:
        allow: List of subject patterns the user is allowed to access
        deny: List of subject patterns the user is denied access to
    """

    allow: list[str] | None = field(default_factory=list)
    deny: list[str] | None = field(default_factory=list)


@dataclass(kw_only=True)
class Resp:
    """Response permissions for request-reply patterns.

    Attributes:
        max: Maximum number of responses allowed
        ttl: Time-to-live for responses in nanoseconds
    """

    max: int
    ttl: int


@dataclass(kw_only=True)
class TimeRange:
    """Time-based access window for time-restricted permissions.

    Attributes:
        start: Start time in RFC3339 format (e.g., "15:04:05")
        end: End time in RFC3339 format (e.g., "17:00:00")
    """

    start: str | None = None
    end: str | None = None


@dataclass(kw_only=True)
class UserData(BaseNats):
    """NATS user permissions and limits.

    This defines what a user is authorized to do on NATS, including
    pub/sub permissions, connection limits, and time-based restrictions.

    Attributes:
        type: Always "user" for user claims
        pub: Publish permissions (allow/deny subjects)
        sub: Subscribe permissions (allow/deny subjects)
        resp: Response permissions for request-reply
        src: Allowed source IP addresses/CIDR ranges
        times: Time-based access windows
        times_location: IANA timezone for time-based restrictions
        subs: Maximum number of subscriptions
        data: Maximum data throughput in bytes/sec
        payload: Maximum message payload size in bytes
        bearer_token: Enable bearer token authentication mode
        allowed_connection_types: Restrict connection types (e.g., STANDARD,
            WEBSOCKET, MQTT)
        issuer_account: Account that issued this user JWT
    """

    type: Literal["user"] = "user"
    pub: PubSubPermissions | None = None
    sub: PubSubPermissions | None = None
    resp: Resp | None = None
    src: list[str] | None = None
    times: list[TimeRange] | None = None
    times_location: str | None = None
    subs: int | None = None
    data: int | None = None
    payload: int | None = None
    bearer_token: bool | None = None
    allowed_connection_types: list[str] | None = None
    issuer_account: str | None = None


@dataclass(kw_only=True)
class UserClaims(BaseClaims[UserData]):
    """Complete JWT claims for a NATS user.

    Combines standard JWT claims with UserData permissions.
    """
