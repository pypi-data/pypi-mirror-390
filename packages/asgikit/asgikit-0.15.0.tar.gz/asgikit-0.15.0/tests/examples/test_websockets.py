import httpx
from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport

from examples.websockets.echo_chat import app


async def test_websocket_chat():
    async with httpx.AsyncClient(transport=ASGIWebSocketTransport(app)) as client:
        response = await client.get("http://localhost")
        assert response.status_code == 200
        assert "<title>WebSocket chat</title>" in response.text

        async with aconnect_ws("http://localhost", client) as ws:
            await ws.send_text("Hello World!")
            message = await ws.receive_text()
            assert message == "Hello World!"
