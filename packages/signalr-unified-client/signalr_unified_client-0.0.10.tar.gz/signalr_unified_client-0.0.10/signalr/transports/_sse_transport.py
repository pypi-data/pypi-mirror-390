import json
import sseclient
from ._transport import Transport
from signalr.security import safe_json_loads, log_security_warning


class ServerSentEventsTransport(Transport):
    def __init__(self, session, connection):
        Transport.__init__(self, session, connection)
        self.__response = None

    def _get_name(self):
        return 'serverSentEvents'

    def start(self):
        connect_url = self._get_url('connect')
        # SSE client handles timeout internally, but we can set session timeout
        timeout = getattr(self._connection, 'request_timeout', 30.0) or 30.0
        self.__response = iter(sseclient.SSEClient(connect_url, session=self._session))
        self._session.get(self._get_url('start'), timeout=timeout)

        def _receive():
            try:
                notification = next(self.__response)
            except StopIteration:
                return
            except Exception as ex:
                try:
                    self._connection.error.fire(ex)
                except Exception:
                    pass
                return
            else:
                if notification.data != 'initialized':
                    self._handle_notification(notification.data)

        return _receive

    def send(self, data):
        timeout = getattr(self._connection, 'request_timeout', 30.0) or 30.0
        response = self._session.post(self._get_url('send'), data={'data': json.dumps(data)}, timeout=timeout)
        try:
            # Decode response content if it's bytes
            content = response.content
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            parsed = safe_json_loads(content)
        except ValueError as e:
            log_security_warning(
                "JSON parsing limit exceeded in SSE transport response",
                exc_info=e
            )
            return
        except json.JSONDecodeError as e:
            log_security_warning(
                "Invalid JSON in SSE transport response",
                exc_info=e
            )
            return
        except Exception as e:
            log_security_warning(
                "Unexpected error parsing SSE transport response",
                exc_info=e
            )
            return
        self._connection.received.fire(**parsed)

    def close(self):
        try:
            timeout = getattr(self._connection, 'request_timeout', 30.0) or 30.0
            self._session.get(self._get_url('abort'), timeout=timeout)
        except Exception:
            pass
