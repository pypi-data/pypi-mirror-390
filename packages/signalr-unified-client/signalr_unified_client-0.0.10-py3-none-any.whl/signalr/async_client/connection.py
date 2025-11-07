import asyncio
import json
from urllib.parse import urlparse, urlunparse

import httpx
import websockets

from signalr.events import EventHook
from signalr.protocols.classic import ClassicProtocolAdapter
from signalr.protocols.core import CoreProtocolAdapter
from signalr.security import (
    log_security_error, log_security_warning, validate_url,
    validate_query_params, ValidationError, check_ssl_configuration
)


class AsyncConnection:
    protocol_version = '1.5'

    def __init__(self, url, client: httpx.AsyncClient | None = None, sslopt=None, protocol=None, core_protocol='json', access_token_factory=None):
        # Validate URL
        is_valid, error_msg = validate_url(url)
        if not is_valid:
            raise ValueError(f"Invalid URL: {error_msg}")
        self.url = url
        self.qs = {}
        self.token = None
        self.id = None
        self.data = None
        self.received = EventHook()
        self.error = EventHook()
        self.starting = EventHook()
        self.stopping = EventHook()
        self.exception = EventHook()
        # Security: Check SSL configuration and warn about insecure settings
        if sslopt:
            check_ssl_configuration(sslopt)
        self.sslopt = sslopt
        self.started = False
        self._protocol_hint = protocol
        self._protocol_adapter = None
        self._client = client or httpx.AsyncClient()
        self._ws = None
        self._recv_task = None
        self._stop_event = asyncio.Event()
        # Reconnect and keepalive
        self.reconnect = True
        self.reconnect_max_attempts = 5
        self.reconnect_initial_backoff = 1.0
        self.reconnect_max_backoff = 30.0
        self.ping_interval = None  # seconds; passed to websockets
        # Timeout configuration
        self.request_timeout = 30.0  # seconds; timeout for HTTP requests
        self.connection_timeout = 300.0  # seconds; absolute connection timeout
        self.idle_timeout = 60.0  # seconds; idle timeout
        self._last_activity_time = None
        # Core specifics and send queue
        self._core_hub_name = None
        self._send_queue = asyncio.Queue(maxsize=100)
        self._send_queue_expiry = 300.0  # seconds; messages expire after 5 minutes
        self._core_use_msgpack = (core_protocol == 'messagepack')
        self.access_token_factory = access_token_factory

    def _get_base_url(self, action, **kwargs):
        args = kwargs.copy()
        args.update(self.qs)
        args['clientProtocol'] = self.protocol_version
        
        # Validate query parameters
        try:
            validated_args = validate_query_params(args)
        except ValidationError as e:
            log_security_error(
                "Invalid query parameters in URL construction",
                exc_info=e,
                action=action
            )
            raise ValueError(f"Invalid query parameters: {str(e)}") from e
        
        query = '&'.join([f"{k}={httpx.QueryParams({k: v})[k]}" for k, v in validated_args.items()])
        return f"{self.url}/{action}?{query}"

    def _ws_url_from(self, http_url):
        parsed = urlparse(http_url)
        scheme = 'wss' if parsed.scheme == 'https' else 'ws'
        return urlunparse((scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))

    async def start(self):
        self.starting.fire()
        negotiate_url = self._get_base_url('negotiate', connectionData=self.data)
        headers = {}
        token = self._get_access_token()
        if token:
            headers['Authorization'] = f'Bearer {token}'
        timeout = httpx.Timeout(self.request_timeout, connect=self.request_timeout)
        r = await self._client.get(negotiate_url, headers=headers or None, timeout=timeout)
        r.raise_for_status()
        negotiate_data = r.json()

        # Pick protocol
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
        try:
            adapter.on_negotiate(negotiate_data, self)
        except (KeyError, ValueError, TypeError) as e:
            log_security_warning(
                "Protocol negotiation error during adapter setup",
                exc_info=e,
                protocol_hint=self._protocol_hint
            )
        except Exception as e:
            log_security_error(
                "Unexpected error during protocol negotiation",
                exc_info=e
            )
        if isinstance(adapter, CoreProtocolAdapter) and not self._core_hub_name:
            try:
                p = urlparse(self.url)
                path = p.path.rstrip('/')
                self._core_hub_name = path.split('/')[-1] if path else None
            except (AttributeError, ValueError) as e:
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

        # Connect WebSocket
        connect_url = self._get_base_url('connect', connectionToken=self.token, connectionData=self.data)
        ws_url = self._ws_url_from(connect_url)
        # Security: Access tokens are sent via Authorization headers only,
        # not in URL query parameters to prevent exposure in logs/history
        token = self._get_access_token()
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        # Note: sslopt not directly used by websockets; users can set SSL context later
        self._ws = await websockets.connect(ws_url, extra_headers=headers, ping_interval=self.ping_interval)

        # Core handshake if needed
        handshake_text = getattr(adapter, 'handshake_text', None)
        if handshake_text:
            await self._ws.send(handshake_text)

        # Classic requires a start request
        if isinstance(adapter, ClassicProtocolAdapter):
            start_url = self._get_base_url('start', transport='webSockets', connectionToken=self.token, connectionData=self.data)
            timeout = httpx.Timeout(self.request_timeout, connect=self.request_timeout)
            await self._client.get(start_url, timeout=timeout)

        self._stop_event.clear()
        self._last_activity_time = asyncio.get_event_loop().time()
        self._recv_task = asyncio.create_task(self._recv_loop())
        self.started = True
        
        # Check idle timeout periodically in background (async)
        if self.idle_timeout:
            async def idle_timeout_checker():
                while not self._stop_event.is_set():
                    await asyncio.sleep(5)  # Check every 5 seconds
                    if self._stop_event.is_set():
                        break
                    if self._last_activity_time and self.idle_timeout:
                        current_time = asyncio.get_event_loop().time()
                        time_since_activity = current_time - self._last_activity_time
                        if time_since_activity > self.idle_timeout:
                            log_security_warning(
                                f"Connection idle timeout ({self.idle_timeout}s) exceeded",
                                idle_time=time_since_activity
                            )
                            self._stop_event.set()
                            break
            asyncio.create_task(idle_timeout_checker())

    async def _recv_loop(self):
        backoff = self.reconnect_initial_backoff
        attempts = 0
        while not self._stop_event.is_set():
            try:
                # Set timeout for WebSocket receive
                message = await asyncio.wait_for(self._ws.recv(), timeout=self.request_timeout)
                # Update activity timestamp
                self._last_activity_time = asyncio.get_event_loop().time()
            except (ConnectionError, OSError, TimeoutError, websockets.exceptions.ConnectionClosed, asyncio.TimeoutError) as ex:
                # Network errors are expected during connection issues
                try:
                    self.exception.fire(ex)
                except Exception:
                    pass
                log_security_warning(
                    "WebSocket connection error",
                    exc_info=ex,
                    attempt=attempts
                )
                if not self.reconnect or self._stop_event.is_set():
                    break
                attempts += 1
                if attempts > self.reconnect_max_attempts:
                    log_security_error(
                        "Max reconnection attempts reached",
                        attempt=attempts
                    )
                    break
                # reconnect
                try:
                    await self._reconnect()
                    backoff = self.reconnect_initial_backoff
                    attempts = 0
                    continue
                except (ConnectionError, OSError, TimeoutError) as e:
                    log_security_warning(
                        "Reconnection attempt failed",
                        exc_info=e,
                        attempt=attempts
                    )
                    await asyncio.sleep(backoff)
                    backoff = min(self.reconnect_max_backoff, backoff * 2)
                    continue
                except Exception as e:
                    log_security_error(
                        "Unexpected error during reconnection",
                        exc_info=e,
                        attempt=attempts
                    )
                    await asyncio.sleep(backoff)
                    backoff = min(self.reconnect_max_backoff, backoff * 2)
                    continue
            except Exception as ex:
                # Unexpected errors
                log_security_error(
                    "Unexpected error in receive loop",
                    exc_info=ex
                )
                try:
                    self.exception.fire(ex)
                except Exception:
                    pass
                if not self.reconnect or self._stop_event.is_set():
                    break
            try:
                parsed = self._protocol_adapter.parse_incoming_raw(message)
            except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as e:
                log_security_warning(
                    "Message parsing error - possible malformed or malicious message",
                    exc_info=e
                )
                parsed = []
            except Exception as e:
                log_security_error(
                    "Unexpected error parsing incoming message",
                    exc_info=e
                )
                parsed = []
            for event in parsed:
                try:
                    if isinstance(event, dict) and 'type' in event:
                        t = event.get('type')
                        if t == 1:
                            hub_name = self._core_hub_name or ''
                            classic_event = {'M': [{'H': hub_name, 'M': event.get('target'), 'A': event.get('arguments', [])}]}
                            self.received.fire(**classic_event)
                            continue
                        if t == 7:
                            err = event.get('error') or 'closed'
                            self.received.fire(**{'E': err})
                            continue
                    self.received.fire(**event)
                except (KeyError, TypeError, ValueError) as ex:
                    log_security_warning(
                        "Error processing event - possible malformed message",
                        exc_info=ex
                    )
                    try:
                        self.exception.fire(ex)
                    except Exception:
                        pass
                except Exception as ex:
                    log_security_warning(
                        "Unexpected error in event handler",
                        exc_info=ex
                    )
                    try:
                        self.exception.fire(ex)
                    except Exception:
                        pass
        try:
            await self._ws.close()
        except (ConnectionError, OSError):
            # Connection already closed or error closing - expected
            pass
        except Exception as e:
            log_security_warning(
                "Error closing WebSocket connection",
                exc_info=e
            )

    async def send(self, data):
        # Update activity timestamp
        self._last_activity_time = asyncio.get_event_loop().time()
        
        # Encode Core / Classic appropriately
        payload = self._encode_outgoing(data)
        try:
            await self._ws.send(payload)
        except (ConnectionError, OSError, websockets.exceptions.ConnectionClosed) as e:
            # Network errors - queue message for retry with timestamp
            log_security_warning(
                "WebSocket send error, queueing message",
                exc_info=e
            )
            try:
                # Store with timestamp for expiration
                current_time = asyncio.get_event_loop().time()
                self._send_queue.put_nowait((current_time, data))
            except asyncio.QueueFull:
                log_security_warning(
                    "Send queue full, message dropped",
                    queue_size=self._send_queue.qsize(),
                    queue_limit=self._send_queue.maxsize,
                    expiry_time=self._send_queue_expiry
                )
            except Exception as e:
                log_security_warning(
                    "Error queueing message",
                    exc_info=e
                )
        except Exception as e:
            log_security_error(
                "Unexpected error sending message",
                exc_info=e
            )
            # Try to queue anyway with timestamp
            try:
                current_time = asyncio.get_event_loop().time()
                self._send_queue.put_nowait((current_time, data))
            except Exception:
                pass

    async def close(self):
        self._stop_event.set()
        if self._recv_task:
            try:
                await asyncio.wait_for(self._recv_task, timeout=2.0)
            except Exception:
                pass
        try:
            await self._ws.close()
        except Exception:
            pass
        self.started = False

    async def _reconnect(self):
        # renegotiate and reconnect websocket
        negotiate_url = self._get_base_url('negotiate', connectionData=self.data)
        token = self._get_access_token()
        headers = {'Authorization': f'Bearer {token}'} if token else None
        timeout = httpx.Timeout(self.request_timeout, connect=self.request_timeout)
        r = await self._client.get(negotiate_url, headers=headers, timeout=timeout)
        r.raise_for_status()
        negotiate_data = r.json()
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
        connect_url = self._get_base_url('connect', connectionToken=self.token, connectionData=self.data)
        ws_url = self._ws_url_from(connect_url)
        # Security: Access tokens are sent via Authorization headers only,
        # not in URL query parameters to prevent exposure in logs/history
        try:
            await self._ws.close()
        except (ConnectionError, OSError):
            # Connection already closed - expected
            pass
        except Exception as e:
            log_security_warning(
                "Error closing old WebSocket during reconnect",
                exc_info=e
            )
        extra_headers = {'Authorization': f'Bearer {token}'} if token else None
        self._ws = await websockets.connect(ws_url, ping_interval=self.ping_interval, extra_headers=extra_headers)
        handshake_text = getattr(self._protocol_adapter, 'handshake_text', None)
        if handshake_text:
            await self._ws.send(handshake_text)
        # Flush queued sends (expire old messages)
        try:
            current_time = asyncio.get_event_loop().time()
            expired_count = 0
            valid_items = []
            # Collect all items first
            temp_items = []
            while not self._send_queue.empty():
                temp_items.append(await self._send_queue.get())
            
            # Filter expired items
            for item in temp_items:
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
                    queue_limit=self._send_queue.maxsize,
                    expiry_time=self._send_queue_expiry
                )
            
            # Send valid items
            for item_data in valid_items:
                payload = self._encode_outgoing(item_data)
                await self._ws.send(payload)
        except (ConnectionError, OSError, websockets.exceptions.ConnectionClosed) as e:
            log_security_warning(
                "Network error flushing queued sends during reconnect",
                exc_info=e
            )
        except Exception as e:
            log_security_warning(
                "Error flushing queued sends during reconnect",
                exc_info=e
            )

    def _encode_outgoing(self, data):
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
                        log_security_warning(
                            "MessagePack encoding error, falling back to JSON",
                            exc_info=e
                        )
                return json.dumps(payload) + chr(0x1E)
        except (KeyError, TypeError, ValueError) as e:
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
            log_security_error(
                "Error retrieving access token from factory",
                exc_info=e
            )
            return None
        return None


