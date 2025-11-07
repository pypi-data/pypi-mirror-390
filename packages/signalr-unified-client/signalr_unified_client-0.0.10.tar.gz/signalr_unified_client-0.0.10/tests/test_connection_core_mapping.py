from signalr._connection import Connection
from signalr.protocols.core import CoreProtocolAdapter


def test_core_incoming_invocation_maps_to_hub_event(monkeypatch):
    # Build a connection with core adapter forced
    class DummyTransport:
        def __init__(self, session, connection):
            pass
        def negotiate(self):
            return {"negotiateVersion": 1, "connectionId": "x"}
        def start(self):
            return lambda: None
        def send(self, data):
            pass
        def close(self):
            pass

    # Monkeypatch AutoTransport in module to use DummyTransport
    import signalr.transports
    monkeypatch.setattr(signalr.transports, 'AutoTransport', DummyTransport)

    c = Connection("http://localhost/chatHub", session=None, protocol='core')
    c._protocol_adapter = CoreProtocolAdapter()
    # Derive hub name from URL (normally done in start())
    from urllib.parse import urlparse
    p = urlparse(c.url)
    path = p.path.rstrip('/')
    c._core_hub_name = path.split('/')[-1] if path else None
    events = []
    def handler(**kwargs):
        events.append(kwargs)
    c.received += handler

    # Core invocation message
    frame = {"type": 1, "target": "newMessageReceived", "arguments": ["hi"]}
    text = __import__('json').dumps(frame) + chr(0x1E)
    c._handle_raw_message(text)

    assert events and 'M' in events[0]
    inner = events[0]['M'][0]
    assert inner['H'] == 'chatHub'
    assert inner['M'] == 'newMessageReceived'
    assert inner['A'] == ["hi"]


