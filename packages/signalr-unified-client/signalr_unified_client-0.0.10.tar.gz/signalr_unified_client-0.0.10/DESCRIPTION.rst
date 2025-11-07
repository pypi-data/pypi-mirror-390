signalr-unified-client
======================

Unified Python client for Microsoft SignalR supporting:
- Classic ASP.NET SignalR 2.x
- ASP.NET Core SignalR (JSON and MessagePack)

Features:
- Thread-based implementation (no gevent dependency)
- Optional asyncio support
- Comprehensive security features (input validation, JSON limits, SSL warnings)
- TLS, proxies, reconnect with backoff, and bearer token authentication
- Resource limits and timeout controls

Requirements
------------

Install requirements by running::

    pip install -r requirements

Or install from PyPI::

    pip install signalr-unified-client

Compatibility
-------------

- Python: 3.8–3.13
- Servers:
  - Classic ASP.NET SignalR 2.x: supported (SSE + WebSockets)
  - ASP.NET Core SignalR: JSON and MessagePack over WebSockets


Usage
-----
Here is sample usage::

    from requests import Session
    from signalr import Connection

    with Session() as session:
        # Create a connection (URL is validated automatically)
        connection = Connection("http://localhost:5000/signalr", session)
        
        # Configure timeouts and resource limits (optional)
        connection.connection_timeout = 600.0  # 10 minutes
        connection.idle_timeout = 120.0  # 2 minutes
        connection.max_hubs = 10

        # Get chat hub (hub name is validated)
        chat = connection.register_hub('chat')

        # Start a connection
        connection.start()

        # Create new chat message handler
        def print_received_message(data):
            print('received: ', data)

        # Create new chat topic handler
        def print_topic(topic, user):
            print('topic: ', topic, user)

        # Create error handler
        def print_error(error):
            print('error: ', error)

        # Receive new chat messages from the hub (method name is validated)
        chat.client.on('newMessageReceived', print_received_message)

        # Change chat topic
        chat.client.on('topicChanged', print_topic)

        # Process errors
        connection.error += print_error

        # Start connection, optionally can be connection.start()
        with connection:

            # Post new message (method name is validated)
            chat.server.invoke('send', 'Python is here')

            # Change chat topic
            chat.server.invoke('setTopic', 'Welcome python!')

            # Invoke server method that throws error
            chat.server.invoke('requestError')

            # Post another message
            chat.server.invoke('send', 'Bye-bye!')

            # Wait a second before exit
            connection.wait(1)

Security
--------
The library includes comprehensive security features:

- **Input Validation**: All user inputs (URLs, hub names, method names, query parameters) are validated
- **JSON Size Limits**: Maximum 1MB message size and 32-level nesting depth
- **SSL Security**: Automatic warnings for insecure SSL configurations
- **Resource Limits**: Connection timeouts, idle timeouts, and message queue limits
- **Header Validation**: CRLF injection prevention
- **Security Logging**: Events logged to ``signalr.security`` logger

See ``docs/CONFIG.md`` and ``docs/USAGE.md`` for detailed security configuration.

