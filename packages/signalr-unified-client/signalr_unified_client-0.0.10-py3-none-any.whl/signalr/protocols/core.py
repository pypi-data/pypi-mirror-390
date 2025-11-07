import json
try:
    import msgpack  # optional
except Exception:  # pragma: no cover
    msgpack = None

from .base import ProtocolAdapter
from signalr.security import safe_json_loads, log_security_warning


class CoreProtocolAdapter(ProtocolAdapter):
    """Adapter scaffold for ASP.NET Core SignalR protocol (JSON variant).

    Note: Full implementation will be provided in the implement-core-json task.
    For now, this adapter only participates in negotiate detection and
    connection identity wiring.
    """

    def __init__(self, use_messagepack=False):
        self.use_messagepack = bool(use_messagepack and msgpack is not None)

    @classmethod
    def accept(cls, negotiate_json):
        if not isinstance(negotiate_json, dict):
            return False
        # Core negotiate typically includes 'negotiateVersion' and 'availableTransports'
        if 'negotiateVersion' in negotiate_json:
            return True
        # Some servers may not include negotiateVersion but have 'availableTransports'
        core_keys = {'availableTransports', 'connectionId'}
        return core_keys.issubset(negotiate_json.keys()) and 'ConnectionToken' not in negotiate_json

    def on_negotiate(self, negotiate_json, connection):
        # Core uses 'connectionId'; tokens/authorization are handled differently
        connection.id = negotiate_json.get('connectionId') or negotiate_json.get('ConnectionId')
        # Classic-specific fields remain unset here

    def parse_incoming_text(self, text):
        # Split on ASCII Record Separator (0x1e)
        if not text:
            return []
        sep = chr(0x1E)
        frames = text.split(sep)
        results = []
        for frame in frames:
            if not frame:
                continue
            try:
                obj = safe_json_loads(frame)
            except ValueError as e:
                # Size or depth limit exceeded
                log_security_warning(
                    "JSON parsing limit exceeded in core protocol frame",
                    exc_info=e
                )
                continue
            except json.JSONDecodeError as e:
                # Invalid JSON
                log_security_warning(
                    "Invalid JSON in core protocol frame",
                    exc_info=e
                )
                continue
            except Exception as e:
                log_security_warning(
                    "Unexpected error parsing JSON in core protocol frame",
                    exc_info=e
                )
                continue
            # Handshake response is an object without 'type' (may have 'error')
            if 'type' not in obj:
                # Ignore handshake ack for now
                continue
            # For now, surface the core JSON message as-is; hub layer will be extended later
            results.append(obj)
        return results

    @property
    def handshake_text(self):
        # Client handshake payload for Core JSON protocol
        protocol_name = "messagepack" if self.use_messagepack else "json"
        return json.dumps({"protocol": protocol_name, "version": 1}) + chr(0x1E)

    def parse_incoming_raw(self, raw):
        if not self.use_messagepack:
            return super().parse_incoming_raw(raw)
        if msgpack is None:
            return []
        if raw is None:
            return []
        results = []
        if isinstance(raw, bytes):
            # Some servers may concatenate multiple msgpack messages; attempt iterative unpack
            try:
                um = msgpack.Unpacker(raw=False)
                um.feed(raw)
                for obj in um:
                    if isinstance(obj, dict):
                        results.append(obj)
                return results
            except Exception:
                try:
                    obj = msgpack.unpackb(raw, raw=False)
                    if isinstance(obj, dict):
                        return [obj]
                except Exception:
                    return []
        # Fallback to text path
        try:
            text = raw.decode('utf-8') if isinstance(raw, (bytes, bytearray)) else str(raw)
        except Exception:
            return []
        return self.parse_incoming_text(text)


