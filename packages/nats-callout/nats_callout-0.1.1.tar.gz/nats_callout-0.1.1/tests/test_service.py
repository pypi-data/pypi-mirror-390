from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import nkeys
import pytest
from nacl.signing import SigningKey

from nats_callout.claims import (
    AuthRequestClaims,
    AuthRequestData,
    AuthResponseClaims,
    AuthResponseData,
    UserClaims,
    UserData,
)
from nats_callout.claims.authorization_request import (
    ClientInfo,
    ConnectOpts,
    ServerID,
)
from nats_callout.encoder import AdaptixEncoder, BaseEncoder
from nats_callout.exceptions import (
    AuthError,
    InvalidServerPublicKeyError,
    ServerSignatureVerificationError,
)
from nats_callout.service import BaseAuthCalloutService


class MockAdaptixEncoder(AdaptixEncoder):
    """Mock encoder for testing that properly handles json_loads/json_dumps."""

    def __init__(self):
        import json
        super().__init__()
        self.json_loads = lambda x: x if isinstance(x, dict) else json.loads(x)
        self.json_dumps = json.dumps


class ConcreteAuthCalloutService(BaseAuthCalloutService):
    """Concrete implementation of BaseAuthCalloutService for testing."""

    def __init__(self, nkey_seed: str | bytes, account: str):
        self.nkey_seed = nkey_seed
        self.account = account
        self.encoder = MockAdaptixEncoder()
        self._auth_handler = None

    @property
    def _encoder_with_kp(self):
        """Ensure encoder has keypair set."""
        self.encoder.kp = self._key_pair
        return self.encoder

    def _encode_auth_response(self, auth_response):
        return self._encoder_with_kp.encode(auth_response)

    def _encode_user_claims(self, user_claims):
        return self._encoder_with_kp.encode(user_claims)

    async def _handle_auth_request_data(
        self,
        auth_request_data: AuthRequestData,
    ) -> UserData:
        if self._auth_handler:
            return await self._auth_handler(auth_request_data)
        # Default implementation
        return UserData(
            pub=None,
            sub=None,
        )


@pytest.fixture
def nkey_seed():
    """Generate a valid account NKey seed for testing."""
    signing_key = SigningKey.generate()
    seed = nkeys.encode_seed(bytes(signing_key), nkeys.PREFIX_BYTE_ACCOUNT)
    return seed.decode()


@pytest.fixture
def service(nkey_seed):
    """Create a test service instance."""
    return ConcreteAuthCalloutService(
        nkey_seed=nkey_seed,
        account="ACCOUNT123",
    )


@pytest.fixture
def auth_request_data():
    """Create sample auth request data."""
    return AuthRequestData(
        server_id=ServerID(
            name="test-server",
            host="localhost",
            id="SERVER123",
            version="2.10.0",
        ),
        user_nkey="UABC123",
        client_info=ClientInfo(
            host="192.168.1.1",
            id=1,
            user="testuser",
        ),
        connect_opts=ConnectOpts(
            protocol=1,
            user="testuser",
        ),
    )


@pytest.fixture
def auth_request_claims(auth_request_data):
    """Create sample auth request claims."""
    return AuthRequestClaims(
        iss="SERVER_PUBLIC_KEY",
        sub="test-subject",
        aud="test-audience",
        iat=int(datetime.now().timestamp()),
        nats=auth_request_data,
    )


class TestBaseAuthCalloutServiceProperties:
    """Tests for property methods and caching."""

    def test_nkey_seed_property_with_string(self, nkey_seed):
        """Test _nkey_seed property converts string to bytes."""
        service = ConcreteAuthCalloutService(
            nkey_seed=nkey_seed,
            account="TEST",
        )

        result = service._nkey_seed

        assert isinstance(result, bytes)
        assert result == nkey_seed.encode()

    def test_nkey_seed_property_with_bytes(self, nkey_seed):
        """Test _nkey_seed property keeps bytes as-is."""
        seed_bytes = nkey_seed.encode()
        service = ConcreteAuthCalloutService(
            nkey_seed=seed_bytes,
            account="TEST",
        )

        result = service._nkey_seed

        assert isinstance(result, bytes)
        assert result == seed_bytes

    def test_nkey_seed_property_is_cached(self, service):
        """Test _nkey_seed property is cached."""
        result1 = service._nkey_seed
        result2 = service._nkey_seed

        assert result1 is result2

    def test_get_account(self, service):
        """Test _get_account returns the account."""
        result = service._get_account()

        assert result == "ACCOUNT123"

    def test_key_pair_property(self, service):
        """Test _key_pair property creates KeyPair."""
        result = service._key_pair

        assert isinstance(result, nkeys.KeyPair)

    def test_key_pair_property_is_cached(self, service):
        """Test _key_pair property is cached."""
        result1 = service._key_pair
        result2 = service._key_pair

        assert result1 is result2

    def test_public_key_property(self, service):
        """Test _public_key property returns public key string."""
        result = service._public_key

        assert isinstance(result, str)
        assert len(result) > 0
        # NATS account public keys start with 'A'
        assert result.startswith("A")

    def test_public_key_property_is_cached(self, service):
        """Test _public_key property is cached."""
        result1 = service._public_key
        result2 = service._public_key

        assert result1 is result2


class TestDecodeAuthRequest:
    """Tests for _decode_auth_request method."""

    def test_decode_auth_request_success(self, service):
        """Test successful decoding of auth request."""
        mock_encoder = Mock()
        mock_claims = Mock(spec=AuthRequestClaims)
        mock_encoder.decode_auth_request.return_value = mock_claims
        service.encoder = mock_encoder

        result = service._decode_auth_request("test_jwt_token")

        assert result == mock_claims
        mock_encoder.decode_auth_request.assert_called_once_with(
            "test_jwt_token"
        )

    def test_decode_auth_request_invalid_signature(self, service):
        """Test decoding with invalid signature raises AuthError."""
        mock_encoder = Mock()
        mock_encoder.decode_auth_request.side_effect = (
            ServerSignatureVerificationError()
        )
        service.encoder = mock_encoder

        with pytest.raises(AuthError) as exc_info:
            service._decode_auth_request("test_jwt_token")

        assert exc_info.value.message == "Invalid signature"

    def test_decode_auth_request_invalid_public_key(self, service):
        """Test decoding with invalid public key raises AuthError."""
        mock_encoder = Mock()
        mock_encoder.decode_auth_request.side_effect = (
            InvalidServerPublicKeyError()
        )
        service.encoder = mock_encoder

        with pytest.raises(AuthError) as exc_info:
            service._decode_auth_request("test_jwt_token")

        assert exc_info.value.message == "Invalid server public key"


class TestEncodeMethodsService:
    """Tests for encoding methods."""

    def test_encode_auth_response(self, service):
        """Test encoding auth response."""
        mock_encoder = Mock()
        mock_encoder.encode.return_value = "encoded_jwt"
        service.encoder = mock_encoder

        auth_response = Mock(spec=AuthResponseClaims)
        result = service._encode_auth_response(auth_response)

        assert result == "encoded_jwt"
        mock_encoder.encode.assert_called_once_with(auth_response)

    def test_encode_user_claims(self, service):
        """Test encoding user claims."""
        mock_encoder = Mock()
        mock_encoder.encode.return_value = "encoded_user_jwt"
        service.encoder = mock_encoder

        user_claims = Mock(spec=UserClaims)
        result = service._encode_user_claims(user_claims)

        assert result == "encoded_user_jwt"
        mock_encoder.encode.assert_called_once_with(user_claims)


class TestHandleMethod:
    """Tests for _handle method."""

    @pytest.mark.asyncio
    async def test_handle_creates_proper_claims(
        self,
        service,
        auth_request_claims,
    ):
        """Test _handle creates proper user and auth response claims."""
        # Setup mock handler
        user_data = UserData(
            pub=None,
            sub=None,
        )
        service._auth_handler = AsyncMock(return_value=user_data)

        # Mock encoder to track calls
        mock_encoder = Mock()
        mock_encoder.encode.return_value = "user_jwt_token"
        service.encoder = mock_encoder

        with patch("nats_callout.service.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now

            result = await service._handle(auth_request_claims)

        # Verify result structure
        assert isinstance(result, AuthResponseClaims)
        assert result.iss == service._public_key
        assert result.sub == auth_request_claims.nats.user_nkey
        assert result.aud == auth_request_claims.nats.server_id.id
        assert result.iat == int(mock_now.timestamp())

        # Verify nats data
        assert isinstance(result.nats, AuthResponseData)
        assert result.nats.jwt == "user_jwt_token"
        assert result.nats.type == "authorization_response"
        assert result.nats.version == auth_request_claims.nats.version

    @pytest.mark.asyncio
    async def test_handle_creates_user_claims_with_correct_fields(
        self,
        service,
        auth_request_claims,
    ):
        """Test that _handle creates UserClaims with correct fields."""
        user_data = UserData(
            pub=None,
            sub=None,
        )
        service._auth_handler = AsyncMock(return_value=user_data)

        # Track the user_claims passed to encoder
        encoded_claims = []

        def track_encode(claims):
            if isinstance(claims, UserClaims):
                encoded_claims.append(claims)
            return "jwt_token"

        mock_encoder = Mock()
        mock_encoder.encode.side_effect = track_encode
        service.encoder = mock_encoder

        with patch("nats_callout.service.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            expected_iat = int(mock_now.timestamp())

            await service._handle(auth_request_claims)

        # Check user claims
        assert len(encoded_claims) == 1
        user_claims = encoded_claims[0]
        assert user_claims.aud == "ACCOUNT123"
        assert user_claims.sub == auth_request_claims.nats.user_nkey
        assert user_claims.iss == service._public_key
        assert user_claims.iat == expected_iat
        assert user_claims.exp == expected_iat + 3600  # 1 hour expiry
        assert user_claims.name == auth_request_claims.nats.user_nkey
        assert user_claims.nats == user_data


class TestHandleRawMethod:
    """Tests for _handle_raw method."""

    @pytest.mark.asyncio
    async def test_handle_raw_with_string_body(self, service):
        """Test _handle_raw with string body."""
        mock_encode_response = "encoded_response"

        with patch.object(
            service, "_decode_auth_request"
        ) as mock_decode, patch.object(
            service, "_handle", new_callable=AsyncMock
        ) as mock_handle, patch.object(
            service, "_encode_auth_response"
        ) as mock_encode:
            mock_claims = Mock()
            mock_decode.return_value = mock_claims
            mock_response = Mock()
            mock_handle.return_value = mock_response
            mock_encode.return_value = mock_encode_response

            result = await service._handle_raw("test_jwt")

            assert result == mock_encode_response
            mock_decode.assert_called_once_with("test_jwt")
            mock_handle.assert_called_once_with(mock_claims)
            mock_encode.assert_called_once_with(mock_response)

    @pytest.mark.asyncio
    async def test_handle_raw_with_bytes_body(self, service):
        """Test _handle_raw with bytes body."""
        mock_encode_response = "encoded_response"

        with patch.object(
            service, "_decode_auth_request"
        ) as mock_decode, patch.object(
            service, "_handle", new_callable=AsyncMock
        ) as mock_handle, patch.object(
            service, "_encode_auth_response"
        ) as mock_encode:
            mock_claims = Mock()
            mock_decode.return_value = mock_claims
            mock_response = Mock()
            mock_handle.return_value = mock_response
            mock_encode.return_value = mock_encode_response

            result = await service._handle_raw(b"test_jwt")

            assert result == mock_encode_response
            mock_decode.assert_called_once_with("test_jwt")

    @pytest.mark.asyncio
    async def test_handle_raw_with_auth_error(
        self,
        service,
        auth_request_claims,
    ):
        """Test _handle_raw handles AuthError and returns error response."""
        error_message = "Authentication failed"

        with patch.object(
            service, "_decode_auth_request"
        ) as mock_decode, patch.object(
            service, "_handle", new_callable=AsyncMock
        ) as mock_handle, patch.object(
            service, "_encode_auth_response"
        ) as mock_encode, patch(
            "nats_callout.service.datetime"
        ) as mock_datetime:
            mock_now = datetime(2024, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now

            mock_decode.return_value = auth_request_claims
            mock_handle.side_effect = AuthError(error_message)
            mock_encode.return_value = "error_response_jwt"

            result = await service._handle_raw("test_jwt")

            assert result == "error_response_jwt"

            # Verify error response structure
            call_args = mock_encode.call_args[0][0]
            assert isinstance(call_args, AuthResponseClaims)
            assert call_args.iss == service._public_key
            assert call_args.sub == auth_request_claims.nats.user_nkey
            assert call_args.aud == auth_request_claims.nats.server_id.id
            assert call_args.iat == int(mock_now.timestamp())
            assert call_args.nats.jwt is None
            assert call_args.nats.error == error_message

    @pytest.mark.asyncio
    async def test_handle_raw_error_response_has_no_jwt(
        self,
        service,
        auth_request_claims,
    ):
        """Test that error response has no JWT."""
        with patch.object(
            service, "_decode_auth_request"
        ) as mock_decode, patch.object(
            service, "_handle", new_callable=AsyncMock
        ) as mock_handle, patch.object(
            service, "_encode_auth_response"
        ) as mock_encode:
            mock_decode.return_value = auth_request_claims
            mock_handle.side_effect = AuthError("Test error")
            mock_encode.return_value = "error_jwt"

            await service._handle_raw("test_jwt")

            # Get the response that was encoded
            call_args = mock_encode.call_args[0][0]
            assert call_args.nats.jwt is None
            assert call_args.nats.error == "Test error"


class TestCallMethod:
    """Tests for __call__ method."""

    @pytest.mark.asyncio
    async def test_call_delegates_to_handle_raw(self, service):
        """Test __call__ delegates to _handle_raw."""
        with patch.object(
            service, "_handle_raw", new_callable=AsyncMock
        ) as mock_handle_raw:
            mock_handle_raw.return_value = "response"

            result = await service("test_body")

            assert result == "response"
            mock_handle_raw.assert_called_once_with("test_body")

    @pytest.mark.asyncio
    async def test_call_with_bytes(self, service):
        """Test __call__ with bytes input."""
        with patch.object(
            service, "_handle_raw", new_callable=AsyncMock
        ) as mock_handle_raw:
            mock_handle_raw.return_value = "response"

            result = await service(b"test_body")

            assert result == "response"
            mock_handle_raw.assert_called_once_with(b"test_body")


class TestIntegrationFlow:
    """Integration tests for the full authentication flow."""

    @pytest.mark.asyncio
    async def test_full_success_flow(
        self,
        nkey_seed,
        auth_request_data,
    ):
        """Test complete successful authentication flow."""
        # Create service
        service = ConcreteAuthCalloutService(
            nkey_seed=nkey_seed,
            account="TEST_ACCOUNT",
        )

        # Setup custom handler
        async def custom_handler(data: AuthRequestData) -> UserData:
            return UserData(
                pub=None,
                sub=None,
                subs=100,
            )

        service._auth_handler = custom_handler

        # Create a properly signed request
        server_signing_key = SigningKey.generate()
        server_seed = nkeys.encode_seed(
            bytes(server_signing_key), nkeys.PREFIX_BYTE_SERVER
        )
        server_kp = nkeys.from_seed(server_seed)
        server_encoder = MockAdaptixEncoder()
        server_encoder.kp = server_kp

        auth_request = AuthRequestClaims(
            iss=server_kp.public_key.decode(),
            sub="test-sub",
            aud="test-aud",
            iat=int(datetime.now().timestamp()),
            nats=auth_request_data,
        )

        request_jwt = server_encoder.encode(auth_request)

        # Process request
        response_jwt = await service(request_jwt)

        # Verify response is a valid JWT
        assert isinstance(response_jwt, str)
        assert response_jwt.count(".") == 2

        # Decode and verify response structure
        service_encoder = service.encoder
        service_encoder.kp = service._key_pair
        import jwt as pyjwt

        decoded = pyjwt.decode(
            response_jwt,
            options={"verify_signature": False},
        )

        assert decoded["iss"] == service._public_key
        assert decoded["sub"] == auth_request_data.user_nkey
        assert decoded["aud"] == auth_request_data.server_id.id
        assert decoded["nats"]["type"] == "authorization_response"
        assert decoded["nats"]["jwt"] is not None
        assert "error" not in decoded["nats"] or decoded["nats"]["error"] is None

    @pytest.mark.asyncio
    async def test_full_error_flow(
        self,
        nkey_seed,
        auth_request_data,
    ):
        """Test complete error authentication flow."""
        # Create service
        service = ConcreteAuthCalloutService(
            nkey_seed=nkey_seed,
            account="TEST_ACCOUNT",
        )

        # Setup handler that raises error
        async def failing_handler(data: AuthRequestData) -> UserData:
            raise AuthError("Invalid credentials")

        service._auth_handler = failing_handler

        # Create a properly signed request
        server_signing_key = SigningKey.generate()
        server_seed = nkeys.encode_seed(
            bytes(server_signing_key), nkeys.PREFIX_BYTE_SERVER
        )
        server_kp = nkeys.from_seed(server_seed)
        server_encoder = MockAdaptixEncoder()
        server_encoder.kp = server_kp

        auth_request = AuthRequestClaims(
            iss=server_kp.public_key.decode(),
            sub="test-sub",
            aud="test-aud",
            iat=int(datetime.now().timestamp()),
            nats=auth_request_data,
        )

        request_jwt = server_encoder.encode(auth_request)

        # Process request
        response_jwt = await service(request_jwt)

        # Verify response
        import jwt as pyjwt

        decoded = pyjwt.decode(
            response_jwt,
            options={"verify_signature": False},
        )

        assert decoded["nats"]["jwt"] is None
        assert decoded["nats"]["error"] == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_nkey_seed_as_string_or_bytes(
        self,
        nkey_seed,
        auth_request_data,
    ):
        """Test service works with both string and bytes nkey_seed."""
        # Test with string
        service_str = ConcreteAuthCalloutService(
            nkey_seed=nkey_seed,
            account="TEST",
        )
        assert service_str._public_key.startswith("A")

        # Test with bytes
        service_bytes = ConcreteAuthCalloutService(
            nkey_seed=nkey_seed.encode(),
            account="TEST",
        )
        assert service_bytes._public_key.startswith("A")

        # Both should produce same public key
        assert service_str._public_key == service_bytes._public_key
