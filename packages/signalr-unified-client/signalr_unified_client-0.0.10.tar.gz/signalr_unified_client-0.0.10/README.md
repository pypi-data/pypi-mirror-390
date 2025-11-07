# signalr-unified-client

[![PyPI](https://img.shields.io/pypi/v/signalr-unified-client.svg)](https://pypi.org/project/signalr-unified-client/)
[![Python Versions](https://img.shields.io/pypi/pyversions/signalr-unified-client.svg)](https://pypi.org/project/signalr-unified-client/)
[![License](https://img.shields.io/pypi/l/signalr-unified-client.svg)](LICENSE.md)

Unified Python client for Microsoft SignalR:
- Classic ASP.NET SignalR 2.x
- ASP.NET Core SignalR (JSON and MessagePack) over WebSockets

Keep your existing threaded API and add optional asyncio. Supports TLS, proxies, reconnect with backoff, and bearer token auth. Includes comprehensive security features: input validation, JSON size limits, SSL security warnings, resource limits, and security logging.

## Installation

```bash
pip install signalr-unified-client

# Optional extras
pip install "signalr-unified-client[async]"         # Async client
pip install "signalr-unified-client[core]"          # Core-friendly WebSockets
pip install "signalr-unified-client[core-msgpack]"  # MessagePack support
pip install "signalr-unified-client[dev]"           # Tests
```


#### Requirements

Install requirements by running
```
pip install -r requirements
```


#### Compatibility

- Python: 3.8–3.13
- Servers:
  - Classic ASP.NET SignalR 2.x: supported (SSE + WebSockets)
  - ASP.NET Core SignalR: JSON and MessagePack over WebSockets


#### Usage

```
from requests import Session
from signalr import Connection

with Session() as session:
    ssl_options = {"check_hostname": False}  # optional TLS tweaks for websocket-client
    # protocol can be "classic" | "core" | omitted for autodetect
    connection = Connection("http://localhost:5000/signalr", session, sslopt=ssl_options)

    #get chat hub
    chat = connection.register_hub('chat')

    #start a connection
    connection.start()

    #create new chat message handler
    def print_received_message(data):
        print('received: ', data)

    #create new chat topic handler
    def print_topic(topic, user):
        print('topic: ', topic, user)

    #create error handler
    def print_error(error):
        print('error: ', error)

    #receive new chat messages from the hub
    chat.client.on('newMessageReceived', print_received_message)

    #change chat topic
    chat.client.on('topicChanged', print_topic)

    #process errors
    connection.error += print_error

    #start connection, optionally can be connection.start()
    with connection:

        #post new message
        chat.server.invoke('send', 'Python is here')

        #change chat topic
        chat.server.invoke('setTopic', 'Welcome python!')

        #invoke server method that throws error
        chat.server.invoke('requestError')

        #post another message
        chat.server.invoke('send', 'Bye-bye!')

        #wait a second before exit
        connection.wait(1)
```

##### SSL options with websocket-client (>=1.8.0)

You can forward any `websocket-client` `sslopt` dictionary to control TLS behavior. Examples:

```python
# Disable hostname verification (self-signed certs). 
# WARNING: The library will emit a security warning for insecure configurations.
# Use only in trusted environments (development/testing).
Connection(url, session, sslopt={"check_hostname": False})

# Provide a custom SSLContext
import ssl
ctx = ssl.create_default_context()
ctx.load_verify_locations('my_extra_CAs.cer')
Connection(url, session, sslopt={'context': ctx})
```

**Security Note**: The library automatically detects and warns about insecure SSL configurations. See `docs/CONFIG.md` for details.

##### ASP.NET Core SignalR

Core servers require a handshake on WebSocket connect. This client performs the handshake automatically and frames messages using the 0x1E record separator for JSON (or MessagePack binary when enabled). Force protocol selection:

```python
Connection(url, session, protocol="core", core_protocol="json")      # JSON
Connection(url, session, protocol="core", core_protocol="messagepack")  # MessagePack
```
Notes:
- WebSockets only for Core (no LongPolling)
- Hubs: Core Invocation is mapped to classic-style hub events

##### Access tokens (Core)

```python
def token_factory():
    return "eyJhbGciOi..."  # obtain bearer token

connection = Connection(url, session, protocol="core")
connection.access_token_factory = token_factory
connection.start()
```


#### Sample application

See `examples/` for classic and core chat examples (sync and async).


#### Security Features

The library includes comprehensive security features:

- **Input Validation**: URLs, hub names, method names, and query parameters are validated
- **JSON Size Limits**: 1MB message size limit and 32-level nesting depth to prevent JSON bomb attacks
- **SSL Security**: Automatic detection and warnings for insecure SSL configurations
- **Resource Limits**: Connection timeouts, idle timeouts, maximum hubs per connection, and message queue limits
- **Header Validation**: CRLF injection prevention in HTTP headers
- **Security Logging**: Structured logging for security events via `signalr.security` logger
- **Access Token Security**: Tokens sent only via Authorization headers, never in URLs

See `docs/CONFIG.md` and `docs/USAGE.md` for detailed security configuration options.

#### Building and Releasing

See `docs/BUILD.md` for detailed instructions on:
- Building the package locally
- Running tests
- Creating distribution packages
- Releasing to PyPI

Quick build commands:
```bash
# Install build tools
pip install --upgrade build twine

# Build package
python -m build

# Test release (TestPyPI)
python -m twine upload --repository testpypi dist/*

# Production release (PyPI)
python -m twine upload dist/*
```

#### Troubleshooting

See docs/USAGE.md and docs/CONFIG.md for advanced usage, proxies, TLS, and security configuration.
See docs/BUILD.md for build and release instructions.

## Badges

Badges are configured for PyPI and Python versions. Add your CI badge once the repository is created.

## Maintainer

Current maintainer: Andy Datewood <andy@datewood.net>

## License

Apache-2.0
