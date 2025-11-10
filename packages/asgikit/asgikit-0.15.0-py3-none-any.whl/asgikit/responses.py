import asyncio
import contextlib
import hashlib
import itertools
import json
import mimetypes
import os
from collections.abc import AsyncIterable
from email.utils import formatdate
from http import HTTPStatus
from logging import getLogger
from typing import Any

from asgikit._constants import (
    CONTENT_LENGTH,
    CONTENT_TYPE,
    COOKIES,
    DEFAULT_ENCODING,
    ENCODING,
    HEADERS,
    IS_FINISHED,
    IS_STARTED,
    RESPONSE,
    SCOPE_ASGIKIT,
    STATUS,
)
from asgikit.cookies import Cookies
from asgikit.exceptions import (
    ClientDisconnectError,
    ResponseAlreadyEndedError,
    ResponseAlreadyStartedError,
    ResponseNotStartedError,
)
from asgikit.files import AsyncFile
from asgikit.headers import MutableHeaders

__all__ = ("Response",)

logger = getLogger(__name__)


class Response:
    """Response object used to send responses to the client"""

    __slots__ = ("_scope", "_receive", "_send")

    def __init__(self, scope, receive, send):
        scope.setdefault(SCOPE_ASGIKIT, {})
        scope[SCOPE_ASGIKIT].setdefault(RESPONSE, {})
        scope[SCOPE_ASGIKIT][RESPONSE].setdefault(STATUS, None)
        scope[SCOPE_ASGIKIT][RESPONSE].setdefault(HEADERS, MutableHeaders())
        scope[SCOPE_ASGIKIT][RESPONSE].setdefault(COOKIES, Cookies())
        scope[SCOPE_ASGIKIT][RESPONSE].setdefault(ENCODING, DEFAULT_ENCODING)
        scope[SCOPE_ASGIKIT][RESPONSE].setdefault(IS_STARTED, False)
        scope[SCOPE_ASGIKIT][RESPONSE].setdefault(IS_FINISHED, False)

        self._scope = scope
        self._receive = receive
        self._send = send

    @property
    def status(self) -> HTTPStatus | None:
        return self._scope[SCOPE_ASGIKIT][RESPONSE][STATUS]

    @status.setter
    def status(self, status: HTTPStatus):
        self._scope[SCOPE_ASGIKIT][RESPONSE][STATUS] = status

    @property
    def headers(self) -> MutableHeaders:
        return self._scope[SCOPE_ASGIKIT][RESPONSE][HEADERS]

    @property
    def cookies(self) -> Cookies:
        return self._scope[SCOPE_ASGIKIT][RESPONSE][COOKIES]

    @property
    def media_type(self) -> str | None:
        return self._scope[SCOPE_ASGIKIT][RESPONSE].get(CONTENT_TYPE)

    @media_type.setter
    def media_type(self, value: str):
        self._scope[SCOPE_ASGIKIT][RESPONSE][CONTENT_TYPE] = value

    @property
    def content_length(self) -> int | None:
        return self._scope[SCOPE_ASGIKIT][RESPONSE].get(CONTENT_LENGTH)

    @content_length.setter
    def content_length(self, value: str):
        self._scope[SCOPE_ASGIKIT][RESPONSE][CONTENT_LENGTH] = value

    @property
    def encoding(self) -> str:
        return self._scope[SCOPE_ASGIKIT][RESPONSE][ENCODING]

    @encoding.setter
    def encoding(self, value: str):
        self._scope[SCOPE_ASGIKIT][RESPONSE][ENCODING] = value

    @property
    def is_started(self) -> bool:
        """Tells whether the response is started or not"""

        return self._scope[SCOPE_ASGIKIT][RESPONSE][IS_STARTED]

    def __set_started(self):
        self._scope[SCOPE_ASGIKIT][RESPONSE][IS_STARTED] = True

    @property
    def is_finished(self) -> bool:
        """Tells whether the response is started or not"""

        return self._scope[SCOPE_ASGIKIT][RESPONSE][IS_FINISHED]

    def __set_finished(self):
        self._scope[SCOPE_ASGIKIT][RESPONSE][IS_FINISHED] = True

    def __encode_headers(self) -> list[tuple[bytes, bytes]]:
        if self.media_type is not None:
            if self.media_type.startswith("text/"):
                content_type = f"{self.media_type}; charset={self.encoding}"
            else:
                content_type = self.media_type

            self.headers.set("content-type", content_type)

        if (
            self.content_length is not None
            and not (
                self.status < HTTPStatus.OK
                or self.status in (HTTPStatus.NO_CONTENT, HTTPStatus.NOT_MODIFIED)
            )
            and "content-length" not in self.headers
        ):
            self.headers.set("content-length", str(self.content_length))

        encoded_headers = self.headers.encode()
        encoded_cookies = self.cookies.encode()

        return list(itertools.chain(encoded_headers, encoded_cookies))

    async def start(self):
        """Start the response

        Must be called before calling ``write()`` or ``end()``

        :raise ResponseAlreadyStartedError: If the response is already started
        :raise ResponseAlreadyFinishedError: If the response is finished
        """

        if self.is_finished:
            raise ResponseAlreadyEndedError()

        if self.is_started:
            raise ResponseAlreadyStartedError()

        self.__set_started()

        status = self.status
        headers = self.__encode_headers()

        await self._send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": headers,
            }
        )

    async def write(self, data: bytes | str, *, more_body=False):
        """Write data to the response

        :raise ResponseNotStartedError: If the response is not started
        """

        if self.is_finished:
            raise ResponseAlreadyEndedError()

        if not self.is_started:
            raise ResponseNotStartedError()

        encoded_data = data if isinstance(data, bytes) else data.encode(self.encoding)

        await self._send(
            {
                "type": "http.response.body",
                "body": encoded_data,
                "more_body": more_body,
            }
        )

        if not more_body:
            self.__set_finished()

    async def end(self):
        """Finish the response

        Must be called when no more data will be written to the response

        :raise ResponseNotStartedError: If the response is not started
        :raise ResponseAlreadyEndedError: If the response is already finished
        """

        if self.is_finished:
            raise ResponseAlreadyEndedError

        if not self.is_started:
            raise ResponseNotStartedError()

        await self.write(b"", more_body=False)

    async def send_bytes(
        self,
        content: bytes,
        status=HTTPStatus.OK,
        media_type: str = None,
    ):
        """Respond with the given content and finish the response"""

        self.status = status
        if media_type:
            self.media_type = media_type

        self.content_length = len(content)

        await self.start()
        await self.write(content, more_body=False)

    async def send_text(
        self,
        content: str,
        status=HTTPStatus.OK,
        media_type: str = "text/plain",
    ):
        """Respond with the given content and finish the response"""

        data = content.encode(self.encoding)
        await self.send_bytes(data, status, media_type)

    async def send_json(
        self,
        content: Any,
        status=HTTPStatus.OK,
        media_type: str = "application/json",
    ):
        """Respond with the given content serialized as JSON"""

        data = json.dumps(
            content,
            allow_nan=False,
            indent=None,
            ensure_ascii=False,
            separators=(",", ":"),
        )

        if isinstance(data, str):
            data = data.encode(self.encoding)

        await self.send_bytes(data, status, media_type)

    async def send_status(self, status: HTTPStatus):
        """Respond an empty response with the given status"""

        self.status = status

        await self.start()
        await self.end()

    async def redirect(
        self,
        location: str,
        permanent: bool = False,
    ):
        """Respond with a redirect

        :param location: Location to redirect to
        :param permanent: If true, send permanent redirect (HTTP 308),
            otherwise send a temporary redirect (HTTP 307).
        """

        status = (
            HTTPStatus.TEMPORARY_REDIRECT
            if not permanent
            else HTTPStatus.PERMANENT_REDIRECT
        )

        self.headers.set("location", location)
        await self.send_status(status)

    async def redirect_post_get(self, location: str):
        """Response with HTTP status 303

        Used to send a redirect to a GET endpoint after a POST request, known as post/redirect/get
        https://en.wikipedia.org/wiki/Post/Redirect/Get

        :param location: Location to redirect to
        """

        self.headers.set("location", location)
        await self.send_status(HTTPStatus.SEE_OTHER)

    async def __listen_for_disconnect(self):
        while True:
            try:
                message = await self._receive()
            except Exception:
                logger.exception("error while listening for client disconnect")
                break

            if message["type"] == "http.disconnect":
                break

    @contextlib.asynccontextmanager
    async def writer(
        self,
        status=HTTPStatus.OK,
        media_type: str = None,
    ):
        """Context manager for streaming data to the response

        :raise ClientDisconnectError: If the client disconnects while sending data
        """

        self.status = status

        if media_type:
            self.media_type = media_type

        await self.start()

        client_disconect = asyncio.create_task(self.__listen_for_disconnect())

        async def write(data: bytes | str):
            if client_disconect.done():
                raise ClientDisconnectError()
            await self.write(data, more_body=True)

        try:
            yield write
        finally:
            await self.end()
            client_disconect.cancel()

    async def send_stream(
        self,
        stream: AsyncIterable[bytes | str],
        status=HTTPStatus.OK,
        media_type: str = None,
    ):
        """Respond with the given stream of data

        :raise ClientDisconnectError: If the client disconnects while sending data
        """

        async with self.writer(status, media_type) as write:
            async for chunk in stream:
                await write(chunk)

    async def send_file(
        self,
        path: str | os.PathLike,
        status=HTTPStatus.OK,
        media_type: str = None,
        stat_result: os.stat_result = None,
    ):
        """Send the given file to the response"""

        if status:
            self.status = status

        if media_type:
            self.media_type = media_type
        elif not self.media_type:
            m_type, _ = mimetypes.guess_type(path, strict=False)
            self.media_type = m_type

        file = AsyncFile(path)

        if not stat_result:
            stat_result = await file.stat()

        if not self.content_length:
            self.content_length = stat_result.st_size

        last_modified = formatdate(stat_result.st_mtime, usegmt=True)
        etag_base = str(stat_result.st_mtime) + "-" + str(stat_result.st_size)
        etag = f'"{hashlib.md5(etag_base.encode(), usedforsecurity=False).hexdigest()}"'
        self.headers.set("last-modified", last_modified)
        self.headers.set("etag", etag)

        if "http.response.pathsend" in self._scope.get("extensions", {}):
            await self.start()
            await self._send(
                {
                    "type": "http.response.pathsend",
                    "path": str(path),
                }
            )
            return

        if "http.response.zerocopysend" in self._scope.get("extensions", {}):
            await self.start()
            file = await asyncio.to_thread(open, path, "rb")
            await self._send(
                {
                    "type": "http.response.zerocopysend",
                    "file": file.fileno(),
                }
            )
            return

        try:
            async with file.stream() as stream:
                await self.send_stream(stream)
        except ClientDisconnectError:
            pass
