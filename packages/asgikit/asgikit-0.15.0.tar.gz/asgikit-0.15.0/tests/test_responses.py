import asyncio
from http import HTTPStatus

import pytest

from asgikit.exceptions import (
    ResponseAlreadyStartedError,
    ResponseAlreadyEndedError,
    ResponseNotStartedError,
)
from asgikit.responses import Response
from tests.utils.asgi import HttpSendInspector


async def test_respond_plain_text():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Response(scope, None, inspector)

    await request.send_text("Hello, World!")

    assert inspector.body == "Hello, World!"


async def test_stream():
    async def stream_data():
        yield "Hello, "
        yield "World!"

    inspector = HttpSendInspector()
    scope = {"type": "http", "http_version": "1.1", "headers": []}
    response = Response(scope, None, inspector)
    await response.send_stream(stream_data())

    assert inspector.body == "Hello, World!"


async def test_stream_context_manager():
    inspector = HttpSendInspector()
    scope = {"type": "http", "http_version": "1.1", "headers": []}
    response = Response(scope, None, inspector)

    async with response.writer() as write:
        await write("Hello, ")
        await write("World!")

    assert inspector.body == "Hello, World!"


async def test_respond_file(tmp_path):
    tmp_file = tmp_path / "tmp_file.txt"
    tmp_file.write_text("Hello, World!")

    inspector = HttpSendInspector()
    scope = {"type": "http", "http_version": "1.1", "headers": []}

    async def sleep_receive():
        while True:
            await asyncio.sleep(1000)

    response = Response(scope, sleep_receive, inspector)
    await response.send_file(tmp_file)

    assert inspector.body == "Hello, World!"


async def test_respond_status():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    response = Response(scope, None, inspector)
    await response.send_status(HTTPStatus.IM_A_TEAPOT)

    assert inspector.status == HTTPStatus.IM_A_TEAPOT
    assert inspector.body == ""


async def test_respond_empty():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    response = Response(scope, None, inspector)

    await response.send_status(HTTPStatus.OK)
    assert inspector.status == HTTPStatus.OK
    assert inspector.body == ""


async def test_respond_plain_text_with_encoding():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    response = Response(scope, None, inspector)
    response.encoding = "iso-8859-6"
    await response.send_text("زيت")
    assert inspector.raw_body.decode("iso-8859-6") == "زيت"


async def test_respond_temporary_redirect():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    response = Response(scope, None, inspector)
    await response.send_redirect("/redirect")

    assert inspector.status == HTTPStatus.TEMPORARY_REDIRECT
    assert (b"location", b"/redirect") in inspector.headers


async def test_respond_permanent_redirect():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    response = Response(scope, None, inspector)
    await response.send_redirect("/redirect", permanent=True)

    assert inspector.status == HTTPStatus.PERMANENT_REDIRECT
    assert (b"location", b"/redirect") in inspector.headers


async def test_respond_post_get_redirect():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    response = Response(scope, None, inspector)
    await response.send_redirect_post_get("/redirect")

    assert inspector.status == HTTPStatus.SEE_OTHER
    assert (b"location", b"/redirect") in inspector.headers


async def test_respond_set_header():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    response = Response(scope, None, inspector)
    response.headers.set("name", "value")
    await response.send_status(HTTPStatus.OK)

    assert inspector.status == HTTPStatus.OK
    assert (b"name", b"value") in inspector.headers


async def test_respond_add_header():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    response = Response(scope, None, inspector)
    response.headers.add("name", "value1", "value2")
    await response.send_status(HTTPStatus.OK)

    assert inspector.status == HTTPStatus.OK
    assert (b"name", b"value1, value2") in inspector.headers


async def test_respond_set_cookie():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    response = Response(scope, None, inspector)
    response.cookies.set("name", "value")
    await response.send_status(HTTPStatus.OK)

    assert inspector.status == HTTPStatus.OK
    assert (b"Set-Cookie", b"name=value; HttpOnly; SameSite=lax") in inspector.headers


async def test_call_start_twice_should_fail():
    async def send(_event):
        pass

    response = Response({"type": "http", "headers": []}, None, send)
    await response.start()

    with pytest.raises(ResponseAlreadyStartedError):
        await response.start()


async def test_call_start_on_finished_response_should_fail():
    async def send(_event):
        pass

    response = Response({"type": "http", "headers": []}, None, send)
    await response.start()
    await response.end()

    with pytest.raises(ResponseAlreadyEndedError):
        await response.start()


async def test_call_write_on_without_start_should_fail():
    async def send(_event):
        pass

    response = Response({"type": "http", "headers": []}, None, send)

    with pytest.raises(ResponseNotStartedError):
        await response.write(b"")


async def test_call_write_on_finished_response_should_fail():
    async def send(_event):
        pass

    response = Response({"type": "http", "headers": []}, None, send)
    await response.start()
    await response.end()

    with pytest.raises(ResponseAlreadyEndedError):
        await response.write(b"")


async def test_call_end_without_start_should_fail():
    async def send(_event):
        pass

    response = Response({"type": "http", "headers": []}, None, send)

    with pytest.raises(ResponseNotStartedError):
        await response.end()


async def test_call_end_on_finished_response_should_fail():
    async def send(_event):
        pass

    response = Response({"type": "http", "headers": []}, None, send)
    await response.start()
    await response.end()

    with pytest.raises(ResponseAlreadyEndedError):
        await response.end()
