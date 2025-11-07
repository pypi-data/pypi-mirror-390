import json

from .base import ProtocolAdapter
from signalr.security import safe_json_loads, log_security_warning


class ClassicProtocolAdapter(ProtocolAdapter):
    """Adapter for classic ASP.NET SignalR (2.x) hub protocol.

    Incoming transport frames are plain JSON dictionaries that can be passed
    directly to Connection.received.
    """

    @classmethod
    def accept(cls, negotiate_json):
        return isinstance(negotiate_json, dict) and 'ConnectionToken' in negotiate_json

    def on_negotiate(self, negotiate_json, connection):
        connection.token = negotiate_json.get('ConnectionToken')
        connection.id = negotiate_json.get('ConnectionId')

    def parse_incoming_text(self, text):
        if not text:
            return []
        try:
            data = safe_json_loads(text)
        except ValueError as e:
            # Size or depth limit exceeded
            log_security_warning(
                "JSON parsing limit exceeded in classic protocol",
                exc_info=e
            )
            return []
        except json.JSONDecodeError as e:
            # Invalid JSON
            log_security_warning(
                "Invalid JSON in classic protocol",
                exc_info=e
            )
            return []
        except Exception as e:
            log_security_warning(
                "Unexpected error parsing JSON in classic protocol",
                exc_info=e
            )
            return []
        if isinstance(data, dict):
            return [data]
        return []

    def parse_incoming_raw(self, raw):
        if isinstance(raw, bytes):
            try:
                raw = raw.decode('utf-8')
            except Exception:
                return []
        return self.parse_incoming_text(raw)


