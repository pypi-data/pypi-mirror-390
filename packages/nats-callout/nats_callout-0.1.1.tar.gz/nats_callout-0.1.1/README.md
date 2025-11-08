# nats-callout

A Python library for implementing NATS Auth Callout consumers, enabling dynamic authentication and authorization for NATS clients.

## What is Auth Callout?

Auth callout is a mechanism in NATS that delegates authentication and authorization to an external service, instead of relying only on static configuration. This allows you to integrate existing identity and access systems like databases, OAuth providers, LDAP, or even simple local checks.

It’s especially valuable in dynamic environments (e.g., browser WebSocket clients) where you need to grant fine-grained and time-sensitive permissions to specific subjects, streams, or key-value stores, rather than relying on preconfigured user definitions.

### How it works:

1. A client connects to the NATS server using basic credentials (e.g., token, password).
2. The NATS server issues an authentication request by publishing a message on the system subject: `$SYS.REQ.USER.AUTH`
3. An external **auth consumer** subscribes to this subject, receives the request, and decides if the client is allowed.
4. The consumer replies with an authorization response, including permissions and limitations that will be enforced for that client session.

![](https://docs.nats.io/~gitbook/image?url=https%3A%2F%2F1487470910-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252F-LqMYcZML1bsXrN3Ezg0%252Fuploads%252FZqnH9925NhQ1StzwPi5R%252Fauth-callout-light.png%3Falt%3Dmedia%26token%3D77e72613-ab63-483e-93e3-dfd4a865fb5e&width=768&dpr=4&quality=100&sign=bf2c8a00&sv=2)

---

## Installation

Install with [uv](https://github.com/astral-sh/uv):

```bash
uv add nats-callout
```

Or with pip:
```bash
pip install nats-callout
```

---

## Usage Example (FastStream Framework)

Below is an example of how to use `nats-callout` with [FastStream](https://faststream.dev/) to implement an Auth Callout consumer:

```python
from faststream import FastStream, NatsBroker, Depends
from nats_callout import BaseAuthCalloutService, AdaptixEncoder, AuthError
from nats_callout.claims import AuthRequestData, UserData, PubSubPermissions

broker = NatsBroker("nats://localhost:4222")
app = FastStream(broker)

# encoder for auth callout service
# by default, we use adaptix with standard json encoding
encoder = AdaptixEncoder()

# Implement your own AuthCalloutService
class AuthCalloutService(BaseAuthCalloutService):
    def __init__(
            self,
            nats_config: NatsConfig,
            db_context: DBContext,
    ):
        self.encoder = encoder
        self.nkey_seed = nats_config.nkey_seed
        self.db_context = db_context

    async def _handle_auth_request_data(self, auth_request_data: AuthRequestData) -> UserData:
        connect_opts = auth_request_data.connect_opts

        # any checks here
        token = connect_opts.auth_token
        if not token:
            raise AuthError("no token provided")

        user = await self.db_context.get_user_by_token(token)

        if not user:
            raise AuthError("invalid token")

        user_data = UserData(
            pub=PubSubPermissions(allow=["foo"], deny=[]),
            sub=PubSubPermissions(allow=["bar"], deny=[]),
            version=auth_request_data.version,
            tags=auth_request_data.tags,
        )
        return user_data


# inject your service and other dependencies to the handler conveniently (e.g., using FastStream Depends or Dishka)
@broker.subscriber("$SYS.REQ.USER.AUTH")
async def handle_auth_request(body: str, auth_callout_service: AuthCalloutService):
    response = await auth_callout_service(body)
    return response


if __name__ == "__main__":
    app.run()
```

---

## TODOs

- [ ] Add support for synchronous (sync) callout service
- [ ] Add the possibility to include custom JWT claims (e.g., nbf and others)
- [ ] Make the `adaptix` an optional dependency

---

## Reference

- [NATS Auth Callout](https://docs.nats.io/nats-server/auth_callout)
- [FastStream Framework](https://faststream.dev/)

---

## License

MIT
