import json
from collections.abc import AsyncIterator
from enum import Enum
from typing import Any

from asgikit._constants import SCOPE_ASGIKIT, STATE, WEBSOCKET
from asgikit.exceptions import (
    AsgiException,
    WebSocketException,
    WebSocketStateError,
    WebSocketClosedError,
    WebSocketDisconnect,
)
from asgikit.headers import MutableHeaders
from asgikit.http_context import HttpContext

__all__ = ("WebSocket",)


class WebSocket(HttpContext):
    """Represents a WebSocket connection"""

    class State(Enum):
        """State of the WebSocket connection"""

        NEW = 1
        """Created, not yet accepted"""

        ACCEPTED = 2
        """Websocket accepted"""

        CLOSED = 3
        """Websocket closed"""

    def __init__(self, scope, receive, send):
        super().__init__(scope, receive, send)

        self.asgi_scope[SCOPE_ASGIKIT].setdefault(WEBSOCKET, {})
        self.asgi_scope[SCOPE_ASGIKIT][WEBSOCKET].setdefault(STATE, self.State.NEW)

    @property
    def ws_state(self) -> State:
        """State of the websocket connection"""
        return self.asgi_scope[SCOPE_ASGIKIT][WEBSOCKET][STATE]

    def __set_state(self, state: State):
        self.asgi_scope[SCOPE_ASGIKIT][WEBSOCKET][STATE] = state

    @property
    def subprotocols(self) -> list[str]:
        """Return a list of subprotocols of this WebSocket connection"""
        return self.asgi_scope["subprotocols"]

    async def __connect(self):
        message = await self.asgi_receive()
        if message["type"] != "websocket.connect":
            raise AsgiException(f"Unexpected asgi message: {message['type']}")

    async def accept(
        self,
        subprotocol: str = None,
        headers: dict[str, str] = None,
    ):
        """Accepts the WebSocket connection"""

        assert self.asgi_scope["type"] == "websocket"

        if self.ws_state != self.State.NEW:
            raise WebSocketStateError()

        await self.__connect()

        headers = MutableHeaders(headers or {})

        await self.asgi_send(
            {
                "type": "websocket.accept",
                "subprotocol": subprotocol,
                "headers": list(headers.encode()),
            }
        )

        self.__set_state(self.State.ACCEPTED)

    async def _read(self) -> dict[str, Any]:
        """Receive data from the WebSocket connection

        :raise self.StateError: If the WebSocket state is not ACCEPTED
        :raise WebSocketDisconnectError: if the client disconnect
        """

        if self.ws_state == self.State.NEW:
            raise WebSocketStateError()

        if self.ws_state == self.State.CLOSED:
            raise WebSocketClosedError()

        message = await self.asgi_receive()
        if message["type"] == "websocket.disconnect":
            self.__set_state(self.State.CLOSED)
            raise WebSocketDisconnect(message["code"], message.get("reason"))

        if message["type"] != "websocket.receive":
            raise WebSocketException(f"Invalid message: {message['type']}")

        return message

    async def read(self) -> str | bytes:
        """Read data from the WebSocket connection

        Data can be either str or bytes
        """

        message = await self._read()
        return message.get("text") or message.get("bytes")

    async def iter(self) -> AsyncIterator[str | bytes]:
        """Iterate over data from the WebSocket connection

        Data can be either str or bytes
        """
        try:
            while True:
                yield await self.read()
        except WebSocketDisconnect:
            pass

    async def read_json(self) -> Any:
        """Read data as json from the WebSocket connection"""

        data = await self.read()
        return json.loads(data)

    async def iter_json(self) -> AsyncIterator[Any]:
        """Iterate over data as json from the WebSocket connection"""

        async for data in self.iter():
            yield json.loads(data)

    async def _write(self, message: dict[str, Any]):
        if self.ws_state == self.State.NEW:
            raise WebSocketStateError()

        if self.ws_state == self.State.CLOSED:
            raise WebSocketClosedError()

        await self.asgi_send(message)

    async def write(self, data: str | bytes):
        """Send data to the WebSocket connection

        :raise WebSocketClosedError: If the WebSocket is closed
        """

        key = "text" if isinstance(data, str) else "bytes"
        await self._write(
            {
                "type": "websocket.send",
                key: data,
            }
        )

    async def write_json(self, data: Any):
        """Send data as json to the WebSocket connection

        :raise WebSocketClosedError: If the WebSocket is closed
        """

        json_data = json.dumps(data)
        await self.write(json_data)

    async def close(self, code: int = 1000, reason: str = ""):
        """Close the WebSocket connection

        :raise WebSocketClosedError: If the WebSocket is closed
        """

        if self.ws_state == self.State.CLOSED:
            raise WebSocketClosedError()

        if self.ws_state == self.State.NEW:
            await self.__connect()

        await self.asgi_send(
            {
                "type": "websocket.close",
                "code": code,
                "reason": reason,
            }
        )

        self.__set_state(self.State.CLOSED)
