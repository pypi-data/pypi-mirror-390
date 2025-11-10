from httpx import ASGITransport, AsyncClient

from asgikit.responses import Response


async def test_request_response():
    async def app(scope, receive, send):
        if scope["type"] != "http":
            return

        response = Response(scope, receive, send)
        await response.send_text("Ok")

    async with AsyncClient(transport=ASGITransport(app)) as client:
        client_response = await client.get("http://localhost:8000/")
        assert client_response.text == "Ok"
