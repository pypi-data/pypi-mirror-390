import json
import sys
import re
import threading
import time

if sys.version_info[0] < 3:
    from urlparse import urlparse, urlunparse
else:
    from urllib.parse import urlparse, urlunparse

from websocket import create_connection
from ._transport import Transport
from signalr.security import (
    log_security_error, log_security_warning, validate_headers,
    ValidationError
)


class WebSocketsTransport(Transport):
    def __init__(self, session, connection):
        Transport.__init__(self, session, connection)
        self.ws = None
        self.__requests = {}
        self.__ping_thread = None
        self.__stop_ping = None

    def _get_name(self):
        return 'webSockets'

    @staticmethod
    def __get_ws_url_from(url):
        parsed = urlparse(url)
        scheme = 'wss' if parsed.scheme == 'https' else 'ws'
        url_data = (scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment)

        return urlunparse(url_data)

    def start(self):
        ws_url = self.__get_ws_url_from(self._get_url('connect'))
        # Security: Access tokens are now sent via Authorization headers only,
        # not in URL query parameters to prevent exposure in logs/history
        
        proxy_address = None
        if self._session.proxies and ('https' in self._session.proxies or 'http' in self._session.proxies):
            proxy_address = self._session.proxies.get('https') or self._session.proxies.get('http')
        proxy_data = self.__get_proxy_data(proxy_address)
            
        # Inject Authorization header if token available
        headers = self.__get_headers()
        try:
            token = self._connection._get_access_token()
            if token:
                headers.append('Authorization: Bearer %s' % token)
        except (AttributeError, TypeError) as e:
            log_security_error(
                "Failed to inject Authorization header in WebSocket transport",
                exc_info=e
            )
        except Exception as e:
            log_security_warning(
                "Error during authorization header setup in WebSocket transport",
                exc_info=e
            )

        # Set timeout for WebSocket connection
        timeout = getattr(self._connection, 'connection_timeout', 30.0) or 30.0
        self.ws = create_connection(ws_url,
                                    header=headers,
                                    cookie=self.__get_cookie_str(),
                                    enable_multithread=True,
                                    sslopt=self._connection.sslopt,
                                    timeout=timeout,
                                    http_proxy_host = proxy_data['host'], 
                                    http_proxy_port = proxy_data['port'],
                                    http_proxy_auth = (proxy_data['user'], proxy_data['pass']) if proxy_data['user'] else None)
        
        # Send Core protocol handshake if applicable
        try:
            adapter = getattr(self._connection, '_protocol_adapter', None)
            handshake_text = getattr(adapter, 'handshake_text', None)
            if handshake_text:
                self.ws.send(handshake_text)
        except (AttributeError, OSError, ConnectionError) as e:
            log_security_warning(
                "Error sending Core protocol handshake",
                exc_info=e
            )
        except Exception as e:
            log_security_error(
                "Unexpected error sending Core protocol handshake",
                exc_info=e
            )

        # Start ping keepalive if configured on connection
        try:
            ping_interval = getattr(self._connection, 'ping_interval', None)
            if ping_interval and ping_interval > 0:
                self.__stop_ping = threading.Event()
                def _pinger():
                    while self.ws and not self.__stop_ping.is_set():
                        try:
                            self.ws.ping()
                        except Exception:
                            break
                        self.__stop_ping.wait(ping_interval)
                self.__ping_thread = threading.Thread(target=_pinger, daemon=True)
                self.__ping_thread.start()
        except Exception:
            pass

        # Set timeout for start request
        timeout = getattr(self._connection, 'request_timeout', 30.0) or 30.0
        self._session.get(self._get_url('start'), timeout=timeout)

        def _receive():
            notification = self.ws.recv()
            self._handle_notification(notification)

        return _receive

    def send(self, data):
        try:
            payload = self._connection._encode_outgoing(data)
        except (KeyError, TypeError, ValueError) as e:
            log_security_warning(
                "Error encoding outgoing message, using JSON fallback",
                exc_info=e
            )
            payload = json.dumps(data)
        except Exception as e:
            log_security_error(
                "Unexpected error encoding outgoing message, using JSON fallback",
                exc_info=e
            )
            payload = json.dumps(data)
        try:
            self.ws.send(payload)
        except (ConnectionError, OSError) as e:
            log_security_warning(
                "WebSocket send error",
                exc_info=e
            )
            raise
        except Exception as e:
            log_security_error(
                "Unexpected error sending WebSocket message",
                exc_info=e
            )
            raise
        #thread.sleep() #TODO: inveistage if we should sleep here or not

    def close(self):
        try:
            if self.__stop_ping:
                self.__stop_ping.set()
            if self.__ping_thread and self.__ping_thread.is_alive():
                self.__ping_thread.join(timeout=1.0)
        except Exception as e:
            log_security_warning(
                "Error stopping ping thread",
                exc_info=e
            )
        try:
            self.ws.close()
        except (ConnectionError, OSError):
            # Connection already closed - expected
            pass
        except Exception as e:
            log_security_warning(
                "Error closing WebSocket",
                exc_info=e
            )

    def accept(self, negotiate_data):
        return bool(negotiate_data['TryWebSockets'])

    class HeadersLoader(object):
        def __init__(self, headers):
            self.headers = headers

    def __get_headers(self):
        headers = self._session.headers
        loader = WebSocketsTransport.HeadersLoader(headers)

        if self._session.auth:
            self._session.auth(loader)
        
        # Validate and sanitize headers
        try:
            validated_headers = validate_headers(headers)
        except ValidationError as e:
            log_security_error(
                "Invalid headers detected in WebSocket transport",
                exc_info=e
            )
            # Use original headers but log the issue
            validated_headers = headers
        
        return ['%s: %s' % (name, validated_headers[name]) for name in validated_headers]

    def __get_cookie_str(self):
        return '; '.join([
                             '%s=%s' % (name, value)
                             for name, value in self._session.cookies.items()
                             ])

    def __get_proxy_data(self, proxy_url):        
        result = {'host': None, 'port': None, 'user': None, 'pass': None}
        
        if not proxy_url:
            return result

        try:
            parsed = urlparse(proxy_url if re.match(r'^\w+://', proxy_url) else 'http://' + proxy_url)
            result['host'] = parsed.hostname
            result['port'] = parsed.port
            if parsed.username:
                result['user'] = parsed.username
            if parsed.password:
                result['pass'] = parsed.password
        except (AttributeError, ValueError) as e:
            log_security_warning(
                "Error parsing proxy URL",
                exc_info=e
            )
        except Exception as e:
            log_security_error(
                "Unexpected error parsing proxy URL",
                exc_info=e
            )
        
        return result