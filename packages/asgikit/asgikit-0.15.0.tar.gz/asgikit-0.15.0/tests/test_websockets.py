import copy

import pytest

from asgiref.typing import HTTPScope

from asgikit.exceptions import WebSocketStateError
from asgikit.websockets import WebSocket
from tests.utils.asgi import AsgiReceiveInspector, WebSocketSendInspector


async def test_websocket():
    scope = {
        "type": "websocket",
        "subprotocols": ["stomp"],
        "headers": [],
    }

    receive = AsgiReceiveInspector()
    send = WebSocketSendInspector()

    websocket = WebSocket(scope, receive, send)

    receive.send({"type": "websocket.connect"})

    await websocket.accept(subprotocol="stomp")
    assert send.subprotocol == "stomp"


SCOPE: HTTPScope = {
    "asgi": {
        "version": "3.0",
        "spec_version": "2.3",
    },
    "type": "http",
    "http_version": "1.1",
    "method": "GET",
    "scheme": "http",
    "path": "/",
    "raw_path": b"/",
    "query_string": b"",
    "root_path": "",
    "headers": [(b"custom-header", b"value")],
    "client": None,
    "server": None,
    "extensions": None,
}


async def test_websocket_properties():
    scope = copy.deepcopy(SCOPE)
    scope["headers"] += []
    request = WebSocket(scope, None, None)

    assert request.http_version == "1.1"
    assert request.path == "/"
    assert request.cookies == {}
    assert request.headers == {"custom-header": ["value"]}


async def test_call_when_state_not_new_should_fail():
    scope = {"type": "websocket", "headers": []}

    async def receive():
        return {"type": "websocket.connect"}

    async def send(_event):
        pass

    websocket = WebSocket(scope, receive, send)
    await websocket.accept()

    with pytest.raises(WebSocketStateError):
        await websocket.accept()
