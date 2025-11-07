import json

from signalr.protocols.classic import ClassicProtocolAdapter
from signalr.protocols.core import CoreProtocolAdapter


def test_classic_accept_and_parse():
    negotiate = {"ConnectionToken": "tok", "ConnectionId": "cid", "TryWebSockets": True}
    assert ClassicProtocolAdapter.accept(negotiate)

    msg = {
        "C": "d-123",
        "M": [
            {"H": "chat", "M": "newMessageReceived", "A": ["Hello"]}
        ],
    }
    text = json.dumps(msg)
    parsed = ClassicProtocolAdapter().parse_incoming_text(text)
    assert isinstance(parsed, list) and parsed
    assert parsed[0]["M"][0]["H"] == "chat"


def test_core_accept_and_parse_frames():
    negotiate = {"negotiateVersion": 1, "connectionId": "abc", "availableTransports": []}
    assert CoreProtocolAdapter.accept(negotiate)

    frames = [
        json.dumps({"type": 6}),  # ping
        json.dumps({"type": 1, "target": "Send", "arguments": ["Hello"]}),
    ]
    text = "\x1e".join(frames) + "\x1e"

    parsed = CoreProtocolAdapter().parse_incoming_text(text)
    # Both frames should be surfaced (ping + invocation)
    assert len(parsed) == 2
    assert parsed[1]["target"] == "Send"
