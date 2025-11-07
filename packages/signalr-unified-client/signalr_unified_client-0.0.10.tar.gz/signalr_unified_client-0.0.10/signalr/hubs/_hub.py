from signalr.events import EventHook
from signalr.security import validate_method_name, log_security_error, ValidationError


class Hub:
    def __init__(self, name, connection):
        self.name = name
        self.server = HubServer(name, connection, self)
        self.client = HubClient(name, connection)
        self.error = EventHook()


class HubServer:
    def __init__(self, name, connection, hub):
        self.name = name
        self.__connection = connection
        self.__hub = hub

    def invoke(self, method, *data):
        # Validate method name
        try:
            method = validate_method_name(str(method))
        except ValidationError as e:
            log_security_error(
                "Invalid method name provided",
                exc_info=e,
                method_name=method,
                hub_name=self.name
            )
            raise ValueError(f"Invalid method name: {str(e)}") from e
        
        self.__connection.send({
            'H': self.name,
            'M': method,
            'A': data,
            'I': self.__connection.increment_send_counter()
        })


class HubClient(object):
    def __init__(self, name, connection):
        self.name = name
        self.__handlers = {}

        def handle(**kwargs):
            messages = kwargs['M'] if 'M' in kwargs and len(kwargs['M']) > 0 else {}
            for inner_data in messages:
                hub = inner_data['H'] if 'H' in inner_data else ''
                if hub.lower() == self.name.lower():
                    method = inner_data['M']
                    if method in self.__handlers:
                        arguments = inner_data['A']
                        self.__handlers[method].fire(*arguments)

        connection.received += handle

    def on(self, method, handler):
        # Validate method name
        try:
            method = validate_method_name(str(method))
        except ValidationError as e:
            log_security_error(
                "Invalid method name in event handler registration",
                exc_info=e,
                method_name=method,
                hub_name=self.name
            )
            raise ValueError(f"Invalid method name: {str(e)}") from e
        
        if method not in self.__handlers:
            self.__handlers[method] = EventHook()
        self.__handlers[method] += handler

    def off(self, method, handler):
        # Validate method name
        try:
            method = validate_method_name(str(method))
        except ValidationError as e:
            log_security_error(
                "Invalid method name in event handler removal",
                exc_info=e,
                method_name=method,
                hub_name=self.name
            )
            raise ValueError(f"Invalid method name: {str(e)}") from e
        
        if method in self.__handlers:
            self.__handlers[method] -= handler


class DictToObj:
    def __init__(self, d):
        self.__dict__ = d
