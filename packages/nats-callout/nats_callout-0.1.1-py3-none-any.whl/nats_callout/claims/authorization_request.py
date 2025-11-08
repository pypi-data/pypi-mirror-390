"""Authorization request JWT claims.

This module defines the data structures for authentication requests
sent by the NATS server to the auth callout service.
"""
from dataclasses import dataclass, field
from typing import Literal

from .base import BaseClaims, BaseNats


@dataclass(kw_only=True)
class ServerID:
    """NATS server identification information.

    Attributes:
        name: Server name
        host: Server hostname/IP
        id: Unique server ID
        version: NATS server version
        cluster: Cluster name this server belongs to
        tags: Server tags for categorization
        xkey: Extended encryption keys
    """

    name: str
    host: str
    id: str
    version: str | None = None
    cluster: str | None = None
    tags: list[str] | None = field(default_factory=list)
    xkey: list[str] | None = None


@dataclass(kw_only=True)
class ClientInfo:
    """Information about the connecting client.

    Attributes:
        host: Client hostname/IP address
        id: Client connection ID
        user: Username provided by client
        name: Client connection name
        tags: Client tags
        name_tag: Tag derived from client name
        kind: Client kind/category
        type: Client connection type (STANDARD, WEBSOCKET, etc.)
        mqtt_id: MQTT client ID (for MQTT connections)
        nonce: Random nonce for this connection attempt
    """

    host: str | None = None
    id: int | None = None
    user: str | None = None
    name: str | None = None
    tags: list[str] | None = field(default_factory=list)
    name_tag: str | None = None
    kind: str | None = None
    type: str | None = None
    mqtt_id: str | None = None
    nonce: str | None = None


@dataclass(kw_only=True)
class ConnectOpts:
    """Client connection options from CONNECT message.

    Contains the authentication credentials and metadata provided
    by the client during connection.

    Attributes:
        protocol: NATS protocol version
        jwt: User JWT if provided by client
        nkey: User NKey public key if using NKey auth
        sig: Signature if using NKey auth
        auth_token: Bearer/auth token if provided
        user: Username for basic auth
        pass_: Password for basic auth (note underscore suffix)
        name: Client connection name
        lang: Client library language
        version: Client library version
    """

    protocol: int
    jwt: str | None = None
    nkey: str | None = None
    sig: str | None = None
    auth_token: str | None = None
    user: str | None = None
    pass_: str | None = None
    name: str | None = None
    lang: str | None = None
    version: str | None = None


@dataclass(kw_only=True)
class ClientTLS:
    """TLS connection information for the client.

    Attributes:
        version: TLS version used
        cipher: TLS cipher suite
        certs: Client certificate chain (PEM format)
        verified_chains: Verified certificate chains
    """

    version: str | None = None
    cipher: str | None = None
    certs: list[str] | None = field(default_factory=list)
    verified_chains: list[list[str]] | None = field(default_factory=list)


@dataclass(kw_only=True)
class AuthRequestData(BaseNats):
    """Authorization request data from NATS server.

    Contains all information about the authentication request including
    server info, client info, credentials, and TLS details.

    Attributes:
        type: Always "authorization_request"
        server_id: Information about the NATS server
        user_nkey: User NKey public key
        client_info: Information about the connecting client
        connect_opts: Connection options with credentials
        client_tls: TLS connection details if applicable
        request_nonce: Unique nonce for this auth request
    """

    type: Literal["authorization_request"] = "authorization_request"
    server_id: ServerID
    user_nkey: str
    client_info: ClientInfo
    connect_opts: ConnectOpts
    client_tls: ClientTLS | None = None
    request_nonce: str | None = None


@dataclass(kw_only=True)
class AuthRequestClaims(BaseClaims[AuthRequestData]):
    """Complete JWT claims for an authorization request.

    Combines standard JWT claims with AuthRequestData.
    """
