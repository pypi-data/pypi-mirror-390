class AsgiException(Exception):
    """Generic ASGI exception"""


class HttpException(AsgiException):
    """Generic HTTP exception"""


class ClientDisconnectError(HttpException):
    """Client disconnected"""


class RequestAlreadyConsumedError(HttpException):
    """Tried to consume a request body that is already consumed"""


class ResponseAlreadyStartedError(HttpException):
    """Tried to start a response that has already started"""


class ResponseNotStartedError(HttpException):
    """Interacted with a response that has not yet started"""


class ResponseAlreadyEndedError(HttpException):
    """Interacted with a response that has already ended"""


class WebSocketException(AsgiException):
    pass


class WebSocketClosedError(WebSocketException):
    pass


class WebSocketStateError(WebSocketException):
    pass


class WebSocketDisconnect(WebSocketException):
    def __init__(self, code: int, reason: str | None):
        self.code = code
        self.reason = reason
        super().__init__(f"websocket disconnected: code={code} reason='{reason}'")
