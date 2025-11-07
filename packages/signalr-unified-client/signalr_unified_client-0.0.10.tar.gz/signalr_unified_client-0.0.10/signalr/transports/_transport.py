from abc import abstractmethod
import json
import sys
import threading
if sys.version_info[0] < 3:
    from urllib import quote_plus
else:
    from urllib.parse import quote_plus

from signalr.security import validate_query_params, log_security_error, ValidationError



class Transport:
    def __init__(self, session, connection):
        self._session = session
        self._connection = connection
        # Default timeout for network operations (seconds)
        self._default_timeout = getattr(connection, 'connection_timeout', 30.0) or 30.0

    @abstractmethod
    def _get_name(self):
        pass

    def negotiate(self):
        url = self.__get_base_url(self._connection,
                                  'negotiate',
                                  connectionData=self._connection.data)
        headers = {}
        try:
            token = self._connection._get_access_token()
            if token:
                headers['Authorization'] = 'Bearer %s' % token
        except Exception:
            pass
        # Set timeout for negotiate request
        timeout = getattr(self._connection, 'request_timeout', self._default_timeout)
        negotiate = self._session.get(url, headers=headers if headers else None, timeout=timeout)

        negotiate.raise_for_status()

        return negotiate.json()

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def send(self, data):
        pass

    @abstractmethod
    def close(self):
        pass

    def accept(self, negotiate_data):
        return True

    def _handle_notification(self, message):
        if len(message) > 0:
            # Delegate parsing to connection's protocol adapter
            try:
                handler = getattr(self._connection, '_handle_raw_message', None)
                if handler:
                    handler(message)
            except Exception:
                # Swallow parsing errors here; connection.exception will surface elsewhere
                pass
        #thread.sleep() #TODO: investigate if we should sleep here

    def _get_url(self, action, **kwargs):
        args = kwargs.copy()
        args['transport'] = self._get_name()
        args['connectionToken'] = self._connection.token
        args['connectionData'] = self._connection.data

        return self.__get_base_url(self._connection, action, **args)

    @staticmethod
    def __get_base_url(connection, action, **kwargs):
        args = kwargs.copy()
        args.update(connection.qs)
        args['clientProtocol'] = connection.protocol_version
        
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
        
        query = '&'.join(['{key}={value}'.format(key=key, value=quote_plus(validated_args[key])) for key in validated_args])

        return '{url}/{action}?{query}'.format(url=connection.url,
                                               action=action,
                                               query=query)
