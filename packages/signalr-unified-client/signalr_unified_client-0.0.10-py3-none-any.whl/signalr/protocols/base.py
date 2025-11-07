class ProtocolAdapter:
    """Base protocol adapter for mapping transport messages to Connection events.

    Implementations should provide:
    - accept(negotiate_json: dict) -> bool
    - on_negotiate(negotiate_json: dict, connection) -> None
    - parse_incoming_text(text: str) -> list[dict]
    """

    @classmethod
    def accept(cls, negotiate_json):
        raise NotImplementedError

    def on_negotiate(self, negotiate_json, connection):
        raise NotImplementedError

    def parse_incoming_text(self, text):
        raise NotImplementedError

    # Optional override for binary/text frames
    def parse_incoming_raw(self, raw):
        if isinstance(raw, bytes):
            try:
                raw = raw.decode('utf-8')
            except Exception:
                return []
        return self.parse_incoming_text(raw)


