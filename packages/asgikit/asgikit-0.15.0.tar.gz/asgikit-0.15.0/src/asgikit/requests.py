import asyncio
import json
import re
from collections.abc import AsyncIterator
from http import HTTPMethod
from typing import Any
from urllib.parse import parse_qsl

try:
    from asgikit import forms
except ImportError:
    forms = None

from asgikit._constants import (
    CHARSET,
    CONTENT_LENGTH,
    CONTENT_TYPE,
    DEFAULT_ENCODING,
    IS_CONSUMED,
    REQUEST,
    SCOPE_ASGIKIT,
)

from asgikit.exceptions import (
    AsgiException,
    ClientDisconnectError,
    RequestAlreadyConsumedError,
)
from asgikit.forms import UploadedFile, MultipartNotEnabledError
from asgikit.http_context import HttpContext
from asgikit.multi_value_dict import MultiValueDict

__all__ = ("Request",)

RE_CHARSET = re.compile(r"""charset="?([\w-]+)"?""")

FORM_URLENCODED_CONTENT_TYPE = "application/x-www-urlencoded"
FORM_MULTIPART_CONTENT_TYPE = "multipart/form-data"
FORM_CONTENT_TYPES = (FORM_URLENCODED_CONTENT_TYPE, FORM_MULTIPART_CONTENT_TYPE)


class Request(HttpContext):
    """Represents the incoming request"""

    def __init__(self, scope, receive, send):
        assert scope["type"] == "http"

        super().__init__(scope, receive, send)

        self.asgi_scope[SCOPE_ASGIKIT][REQUEST].setdefault(IS_CONSUMED, False)

    @property
    def method(self) -> HTTPMethod:
        """HTTP method of the request"""

        # pylint: disable=no-value-for-parameter
        return HTTPMethod(self.asgi_scope["method"])

    @property
    def content_type(self) -> str | None:
        """Content type of the request body"""

        if CONTENT_TYPE not in self.asgi_scope[SCOPE_ASGIKIT][REQUEST]:
            if content_type := self.headers.get_first("content-type"):
                content_type = content_type.split(";")[0]
            else:
                content_type = None
            self.asgi_scope[SCOPE_ASGIKIT][REQUEST][CONTENT_TYPE] = content_type
        return self.asgi_scope[SCOPE_ASGIKIT][REQUEST][CONTENT_TYPE]

    @property
    def content_length(self) -> int | None:
        """Content length of the request body"""

        if CONTENT_LENGTH not in self.asgi_scope[SCOPE_ASGIKIT][REQUEST]:
            if content_length := self.headers.get_first("content-length"):
                content_length = int(content_length)
            else:
                content_length = None
            self.asgi_scope[SCOPE_ASGIKIT][REQUEST][CONTENT_LENGTH] = content_length
        return self.asgi_scope[SCOPE_ASGIKIT][REQUEST].get(CONTENT_LENGTH)

    @property
    def charset(self) -> str | None:
        """Charset of the request"""

        if CHARSET not in self.asgi_scope[SCOPE_ASGIKIT][REQUEST]:
            if content_type := self.headers.get_first("content-type"):
                values = RE_CHARSET.findall(content_type)
                charset = values[0] if values else DEFAULT_ENCODING
            else:
                charset = DEFAULT_ENCODING
            self.asgi_scope[SCOPE_ASGIKIT][REQUEST][CHARSET] = charset
        return self.asgi_scope[SCOPE_ASGIKIT][REQUEST][CHARSET]

    @property
    def is_consumed(self) -> bool:
        """Verifies whether the request body is consumed or not"""
        return self.asgi_scope[SCOPE_ASGIKIT][REQUEST][IS_CONSUMED]

    def __set_consumed(self):
        self.asgi_scope[SCOPE_ASGIKIT][REQUEST][IS_CONSUMED] = True

    async def stream(self) -> AsyncIterator[bytes]:
        """Iterate over the bytes of the request body

        :raise RequestBodyAlreadyConsumedError: If the request body is already consumed
        :raise ClientDisconnectError: If the client is disconnected while reading the request body
        """

        if self.is_consumed:
            raise RequestAlreadyConsumedError()

        while True:
            message = await asyncio.wait_for(self.asgi_receive(), 1)

            if message["type"] == "http.request":
                data = message["body"]

                if not message["more_body"]:
                    self.__set_consumed()

                yield data

                if self.is_consumed:
                    break
            elif message["type"] == "http.disconnect":
                raise ClientDisconnectError()
            else:
                raise AsgiException(f"invalid message type: '{message['type']}'")

    async def read_bytes(self) -> bytes:
        """Read the full request body"""

        data = bytearray()

        async for chunk in self.stream():
            data.extend(chunk)

        return bytes(data)

    async def read_text(self, encoding: str = None) -> str:
        """Read the full request body as str"""

        data = await self.read_bytes()
        return data.decode(encoding or self.charset)

    async def read_json(self) -> Any:
        """Read the full request body and parse it as json"""

        if data := await self.read_bytes():
            return json.loads(data)

        return None

    @staticmethod
    def _is_form_multipart(content_type: str) -> bool:
        return content_type.startswith(FORM_MULTIPART_CONTENT_TYPE)

    async def read_form(
        self,
    ) -> MultiValueDict[str | UploadedFile]:
        """Read the full request body and parse it as form encoded"""

        if self._is_form_multipart(self.content_type):
            if not forms:
                raise MultipartNotEnabledError()

            return await forms.process_multipart(
                self.stream(), self.headers.get_first("content-type"), self.charset
            )

        if data := await self.read_text():
            return MultiValueDict(parse_qsl(data, keep_blank_values=True))

        return MultiValueDict()
