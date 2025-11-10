# Asgikit - ASGI Toolkit

Asgikit is a toolkit for building asgi applications and frameworks.

The [examples directory](./examples) contain usage examples of several use cases

## Features:

- Request
  - Headers
  - Cookies
  - Body (bytes, str, json, form, stream)
  - Form
- Response
  - Plain text
  - Json
  - Streaming
  - File
- Websockets

## Example request and response

```python
from asgikit.requests import Request
from asgikit.responses import Response


async def main(scope, receive, send):
    assert scope["type"] == "http"

    request = Request(scope, receive, send)
    response = Response(scope, receive, send)

    # request method
    method = request.method

    # request path
    path = request.path

    # request headers
    headers = request.headers

    # read body as json
    body = await request.read_json()

    data = {
        "lang": "Python",
        "async": True,
        "platform": "asgi",
        "method": method,
        "path": path,
        "headers": dict(headers.items()),
        "body": body,
    }

    # send json response
    await response.send_json(data)
```

## Example websocket

```python
from asgikit.websockets import WebSocket, WebSocketDisconnect


async def app(scope, receive, send):
    assert scope["type"] == "websocket"

    ws = WebSocket(scope, receive, send)
    await ws.accept()

    while True:
        try:
            message = await ws.read()
            await ws.write(message)
        except WebSocketDisconnect:
            print("Client disconnect")
            break
```
