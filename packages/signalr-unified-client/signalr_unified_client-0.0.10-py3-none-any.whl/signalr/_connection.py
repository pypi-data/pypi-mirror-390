import json
import sys
import time
from threading import Thread, Lock, RLock
from signalr.protocols.classic import ClassicProtocolAdapter
from signalr.protocols.core import CoreProtocolAdapter
from signalr.events import EventHook
from signalr.hubs import Hub
from signalr.transports import AutoTransport
from signalr.security import (
    log_security_error, log_security_warning, validate_url,
    sanitize_hub_name, ValidationError, check_ssl_configuration,
    validate_headers
)


class Connection:
    protocol_version = '1.5'

    def __init__(self, url, session, sslopt=None, protocol=None, core_protocol='json'):
        # Validate URL
        is_valid, error_msg = validate_url(url)
        if not is_valid:
            raise ValueError(f"Invalid URL: {error_msg}")
        self.url = url
        self.__hubs = {}
        self.qs = {}
        self.__send_counter = -1
        self.token = None
        self.id = None
        self.data = None
        self.received = EventHook()
        self.error = EventHook()
        self.starting = EventHook()
        self.stopping = EventHook()
        self.exception = EventHook()
        self.is_open = False
        # Optional websocket-client SSL options (e.g., {"check_hostname": False})
        # Security: Check SSL configuration and warn about insecure settings
        if sslopt:
            check_ssl_configuration(sslopt)
        self.sslopt = sslopt
        self.__transport = AutoTransport(session, self)
        self.__listener_thread = None
        self.started = False
        self._protocol_adapter = None
        self._protocol_hint = protocol  # 'classic' | 'core' | None
        self._core_use_msgpack = (core_protocol == 'messagepack')
        # Reconnection and keepalive configuration
        self.reconnect = True
        self.reconnect_max_attempts = 5
        self.reconnect_initial_backoff = 1.0
        self.reconnect_max_backoff = 30.0
        self.ping_interval = None  # seconds; when set, WS transport will ping
        # Core protocol specifics
        self._core_hub_name = None
        # Outgoing send buffering during reconnects
        self._is_reconnecting = False
        self._send_queue = []
        self._send_queue_limit = 100
        self._send_queue_expiry = 300.0  # seconds; messages expire after 5 minutes
        # Thread safety locks
        self._state_lock = RLock()  # For shared state (is_open, _is_reconnecting)
        self._queue_lock = Lock()  # For send queue operations
        # Resource limits
        self.max_hubs = 50  # Maximum number of hubs per connection
        self.connection_timeout = 300.0  # seconds; absolute connection timeout
        self.idle_timeout = 60.0  # seconds; idle timeout (no activity)
        self.request_timeout = 30.0  # seconds; timeout for HTTP requests
        self._last_activity_time = None
        # Optional access token factory for Core (returns string)
        self.access_token_factory = None

        def handle_error(**kwargs):
            error = kwargs["E"] if "E" in kwargs else None
            if error is None:
                return

            self.error.fire(error)

        self.received += handle_error

        self.starting += self.__set_data

    def __set_data(self):
        self.data = json.dumps([{'name': hub_name} for hub_name in self.__hubs])

    def increment_send_counter(self):
        self.__send_counter += 1
        return self.__send_counter

    def start(self):
        self.starting.fire()

        negotiate_data = self.__transport.negotiate()
        # Protocol detection and wiring
        adapter = None
        if self._protocol_hint == 'classic':
            adapter = ClassicProtocolAdapter()
        elif self._protocol_hint == 'core':
            adapter = CoreProtocolAdapter(use_messagepack=self._core_use_msgpack)
        else:
            if ClassicProtocolAdapter.accept(negotiate_data):
                adapter = ClassicProtocolAdapter()
            elif CoreProtocolAdapter.accept(negotiate_data):
                adapter = CoreProtocolAdapter(use_messagepack=self._core_use_msgpack)
            else:
                adapter = ClassicProtocolAdapter()

        self._protocol_adapter = adapter
        # Let adapter set connection identity fields as appropriate
        try:
            adapter.on_negotiate(negotiate_data, self)
        except (KeyError, ValueError, TypeError) as e:
            # Protocol negotiation errors may indicate protocol mismatch
            log_security_warning(
                "Protocol negotiation error during adapter setup",
                exc_info=e,
                protocol_hint=self._protocol_hint
            )
        except Exception as e:
            # Other errors during negotiation should be logged
            log_security_error(
                "Unexpected error during protocol negotiation",
                exc_info=e
            )
        # Inject Authorization header on session for HTTP requests if access token is available
        try:
            token = self._get_access_token()
            if token:
                if 'Authorization' not in self.__transport._session.headers:
                    # Validate and sanitize header before adding
                    try:
                        validated_headers = validate_headers({'Authorization': f'Bearer {token}'})
                        self.__transport._session.headers.update(validated_headers)
                    except ValidationError as e:
                        log_security_error(
                            "Invalid Authorization header value",
                            exc_info=e
                        )
                        # Fallback to original behavior but log the issue
                        self.__transport._session.headers['Authorization'] = f'Bearer {token}'
        except (AttributeError, TypeError) as e:
            # Header injection failures are security-critical
            log_security_error(
                "Failed to inject Authorization header",
                exc_info=e
            )
        except Exception as e:
            log_security_warning(
                "Error during authorization header setup",
                exc_info=e
            )
        # Derive hub name for Core (best-effort from URL path)
        if isinstance(adapter, CoreProtocolAdapter) and not self._core_hub_name:
            try:
                from urllib.parse import urlparse
                p = urlparse(self.url)
                path = p.path.rstrip('/')
                self._core_hub_name = path.split('/')[-1] if path else None
            except (AttributeError, ValueError) as e:
                # URL parsing errors are non-critical
                log_security_warning(
                    "Failed to derive hub name from URL",
                    exc_info=e
                )
                self._core_hub_name = None
            except Exception as e:
                log_security_warning(
                    "Unexpected error deriving hub name",
                    exc_info=e
                )
                self._core_hub_name = None

        listener = self.__transport.start()
        if listener is None:
            raise RuntimeError("Transport start() returned None - transport initialization failed")

        def wrapped_listener():
            nonlocal listener
            backoff = self.reconnect_initial_backoff
            attempts = 0
            while True:
                with self._state_lock:
                    if not self.is_open:
                        break
                try:
                    if listener is None:
                        raise RuntimeError("Listener function is None")
                    listener()
                except:
                    self.exception.fire(*sys.exc_info())
                    with self._state_lock:
                        if not self.reconnect:
                            self.is_open = False
                            break
                        self._is_reconnecting = True
                    attempts += 1
                    with self._state_lock:
                        if attempts > self.reconnect_max_attempts:
                            self.is_open = False
                            break
                    # attempt to re-establish
                    try:
                        negotiate_data = self.__transport.negotiate()
                        # Re-apply adapter on renegotiate
                        try:
                            self._protocol_adapter.on_negotiate(negotiate_data, self)
                        except (KeyError, ValueError) as e:
                            log_security_warning(
                                "Protocol negotiation error during reconnect",
                                exc_info=e
                            )
                        except Exception as e:
                            log_security_error(
                                "Unexpected error during reconnect negotiation",
                                exc_info=e
                            )
                        listener_local = self.__transport.start()
                        if listener_local is None:
                            raise RuntimeError("Transport start() returned None during reconnect")
                        listener = listener_local  # Update listener using nonlocal
                        backoff = self.reconnect_initial_backoff
                        with self._state_lock:
                            self._is_reconnecting = False
                        # Flush queued sends (expire old messages)
                        try:
                            with self._queue_lock:
                                current_time = time.time()
                                expired_count = 0
                                valid_items = []
                                for item in list(self._send_queue):
                                    if isinstance(item, tuple) and len(item) == 2:
                                        # Item with timestamp: (timestamp, data)
                                        item_time, item_data = item
                                        if current_time - item_time < self._send_queue_expiry:
                                            valid_items.append(item_data)
                                        else:
                                            expired_count += 1
                                    else:
                                        # Legacy format without timestamp
                                        valid_items.append(item)
                            
                                if expired_count > 0:
                                    log_security_warning(
                                        f"Expired {expired_count} queued messages during reconnect",
                                        expired_count=expired_count,
                                        queue_limit=self._send_queue_limit,
                                        expiry_time=self._send_queue_expiry
                                    )
                                
                                for item_data in valid_items:
                                    self.__transport.send(item_data)
                                self._send_queue.clear()
                        except (ConnectionError, OSError) as e:
                            log_security_warning(
                                "Network error flushing queued sends during reconnect",
                                exc_info=e
                            )
                        except Exception as e:
                            log_security_warning(
                                "Error flushing queued sends during reconnect",
                                exc_info=e
                            )
                        continue
                    except (ConnectionError, OSError, TimeoutError) as e:
                        # Network errors during reconnect are expected
                        log_security_warning(
                            "Network error during reconnect attempt",
                            exc_info=e,
                            attempt=attempts
                        )
                    except Exception as e:
                        log_security_error(
                            "Unexpected error during reconnect",
                            exc_info=e,
                            attempt=attempts
                        )
                    # backoff with cap
                    time.sleep(backoff)
                    backoff = min(self.reconnect_max_backoff, backoff * 2)

        with self._state_lock:
            self.is_open = True
            self._last_activity_time = time.time()
        self.__listener_thread = Thread(target=wrapped_listener, daemon=False)
        self.__listener_thread.start()
        self.started = True
        
        # Check connection timeout in background
        if self.connection_timeout:
            def timeout_checker():
                start_time = time.time()
                while True:
                    time.sleep(10)  # Check every 10 seconds
                    with self._state_lock:
                        if not self.is_open:
                            break
                        elapsed = time.time() - start_time
                        if elapsed > self.connection_timeout:
                            log_security_warning(
                                f"Connection absolute timeout ({self.connection_timeout}s) exceeded",
                                elapsed_time=elapsed
                            )
                            self.is_open = False
                            break
            timeout_thread = Thread(target=timeout_checker, daemon=True)
            timeout_thread.start()
        
        # Check idle timeout periodically in background
        if self.idle_timeout:
            def idle_timeout_checker():
                while True:
                    time.sleep(5)  # Check every 5 seconds
                    with self._state_lock:
                        if not self.is_open:
                            break
                        if self._last_activity_time and self.idle_timeout:
                            time_since_activity = time.time() - self._last_activity_time
                            if time_since_activity > self.idle_timeout:
                                log_security_warning(
                                    f"Connection idle timeout ({self.idle_timeout}s) exceeded",
                                    idle_time=time_since_activity
                                )
                                self.is_open = False
                                break
            idle_thread = Thread(target=idle_timeout_checker, daemon=True)
            idle_thread.start()

    def _handle_raw_message(self, raw_text):
        # Check idle timeout BEFORE updating timestamp (using previous timestamp)
        current_time = time.time()
        with self._state_lock:
            # Check if idle timeout was exceeded based on previous activity time
            if self._last_activity_time and self.idle_timeout:
                time_since_activity = current_time - self._last_activity_time
                if time_since_activity > self.idle_timeout:
                    log_security_warning(
                        f"Connection idle timeout ({self.idle_timeout}s) exceeded",
                        idle_time=time_since_activity
                    )
                    self.is_open = False
                    return
            # Update activity timestamp after checking
            self._last_activity_time = current_time
        
        if not self._protocol_adapter:
            self._protocol_adapter = ClassicProtocolAdapter()
        try:
            parsed_events = self._protocol_adapter.parse_incoming_raw(raw_text)
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as e:
            # Parse errors are expected for malformed messages
            log_security_warning(
                "Message parsing error - possible malformed or malicious message",
                exc_info=e
            )
            parsed_events = []
        except Exception as e:
            log_security_error(
                "Unexpected error parsing incoming message",
                exc_info=e
            )
            parsed_events = []
        for event in parsed_events:
            try:
                # Map Core messages to classic-like hub events
                if isinstance(event, dict) and 'type' in event:
                    t = event.get('type')
                    if t == 1:  # Invocation
                        hub_name = self._core_hub_name or ''
                        classic_event = {'M': [{'H': hub_name, 'M': event.get('target'), 'A': event.get('arguments', [])}]}
                        self.received.fire(**classic_event)
                        continue
                    if t == 7:  # Close
                        err = event.get('error') or 'closed'
                        self.received.fire(**{'E': err})
                        continue
                    # Ignore other Core types for now
                    continue
                # Classic event
                self.received.fire(**event)
            except (KeyError, TypeError, ValueError) as e:
                # Handler errors for malformed events
                log_security_warning(
                    "Error processing event - possible malformed message",
                    exc_info=e
                )
                self.exception.fire(*sys.exc_info())
            except Exception as e:
                # Surface handler exceptions to the exception hook
                log_security_warning(
                    "Unexpected error in event handler",
                    exc_info=e
                )
                self.exception.fire(*sys.exc_info())

    def wait(self, timeout=30):
        Thread.join(self.__listener_thread, timeout)

    def send(self, data):
        # Update activity timestamp
        with self._state_lock:
            self._last_activity_time = time.time()
            is_reconnecting = self._is_reconnecting
        
        if is_reconnecting:
            with self._queue_lock:
                if len(self._send_queue) < self._send_queue_limit:
                    # Store with timestamp for expiration
                    self._send_queue.append((time.time(), data))
                else:
                    log_security_warning(
                        "Send queue full, message dropped",
                        queue_size=len(self._send_queue),
                        queue_limit=self._send_queue_limit,
                        is_reconnecting=self._is_reconnecting
                    )
            return
        self.__transport.send(data)

    def _encode_outgoing(self, data):
        # For Core, translate classic hub invoke dict to Core InvocationMessage
        try:
            if isinstance(self._protocol_adapter, CoreProtocolAdapter) and isinstance(data, dict) and 'M' in data and 'A' in data and 'I' in data:
                payload = {
                    'type': 1,
                    'target': data.get('M'),
                    'arguments': list(data.get('A', [])),
                    'invocationId': str(data.get('I'))
                }
                if getattr(self._protocol_adapter, 'use_messagepack', False):
                    try:
                        import msgpack
                        return msgpack.packb(payload, use_bin_type=True)
                    except ImportError as e:
                        log_security_warning(
                            "MessagePack not available, falling back to JSON",
                            exc_info=e
                        )
                    except Exception as e:
                        # msgpack may raise various exceptions during encoding
                        log_security_warning(
                            "MessagePack encoding error, falling back to JSON",
                            exc_info=e
                        )
                return json.dumps(payload) + chr(0x1E)
        except (KeyError, TypeError, ValueError) as e:
            # Encoding errors for malformed data
            log_security_warning(
                "Error encoding outgoing message",
                exc_info=e
            )
        except Exception as e:
            log_security_error(
                "Unexpected error encoding outgoing message",
                exc_info=e
            )
        return json.dumps(data)

    def _get_access_token(self):
        try:
            if callable(self.access_token_factory):
                return self.access_token_factory()
        except Exception as e:
            # Token factory errors are security-critical
            log_security_error(
                "Error retrieving access token from factory",
                exc_info=e
            )
            return None
        return None

    def close(self):
        with self._state_lock:
            self.is_open = False
        if self.__listener_thread:
            self.__listener_thread.join(timeout=5.0)
        self.__transport.close()

    def register_hub(self, name):
        # Validate and sanitize hub name
        try:
            name = sanitize_hub_name(name)
        except ValidationError as e:
            log_security_error(
                "Invalid hub name provided",
                exc_info=e,
                hub_name=name
            )
            raise ValueError(f"Invalid hub name: {str(e)}") from e
        
        if name not in self.__hubs:
            if self.started:
                raise RuntimeError(
                    'Cannot create new hub because connection is already started.')
            
            # Check hub limit
            if len(self.__hubs) >= self.max_hubs:
                log_security_error(
                    "Maximum number of hubs exceeded",
                    current_count=len(self.__hubs),
                    max_hubs=self.max_hubs,
                    hub_name=name
                )
                raise RuntimeError(
                    f'Maximum number of hubs ({self.max_hubs}) exceeded. '
                    f'Cannot register additional hubs.'
                )

            self.__hubs[name] = Hub(name, self)
        return self.__hubs[name]

    def hub(self, name):
        return self.__hubs[name]

    def __enter__(self):
        self.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
