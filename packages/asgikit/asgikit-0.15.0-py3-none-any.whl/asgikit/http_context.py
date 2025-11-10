from abc import ABC
import http.cookies
import itertools
from urllib.parse import parse_qsl, unquote_plus
from typing import Any

from asgikit._constants import COOKIES, HEADERS, QUERY, REQUEST, SCOPE_ASGIKIT
from asgikit.headers import Headers
from asgikit.multi_value_dict import MultiValueDict


def _parse_cookie(cookie: str):
    for chunk in cookie.split(";"):
        if "=" in chunk:
            key, val = chunk.split("=", 1)
        else:
            # Assume an empty name per
            # https://bugzilla.mozilla.org/show_bug.cgi?id=169091
            key, val = "", chunk
        key, val = key.strip(), val.strip()
        if key or val:
            # unquote using Python's algorithm.
            # pylint: disable=protected-access
            yield key, http.cookies._unquote(val)


def parse_cookie(cookies: list[str]) -> MultiValueDict[str]:
    values = itertools.chain.from_iterable(_parse_cookie(cookie) for cookie in cookies)
    return MultiValueDict(values)


class HttpContext(ABC):
    """Base class for Request and Websocket

    Provides methods for retrieving basic context of the http connection
    """

    __slots__ = (
        "asgi_scope",
        "asgi_receive",
        "asgi_send",
        "__weakref__",
    )

    def __init__(self, scope, receive, send):
        assert scope["type"] in ("http", "websocket")

        self.asgi_scope = scope
        self.asgi_receive = receive
        self.asgi_send = send

        self.asgi_scope.setdefault(SCOPE_ASGIKIT, {})
        self.asgi_scope[SCOPE_ASGIKIT].setdefault(REQUEST, {})

    @property
    def state(self) -> dict | None:
        """State managed by the ASGI server"""
        return self.asgi_scope.get("state")

    @property
    def http_version(self) -> str:
        """HTTP version"""
        return self.asgi_scope["http_version"]

    @property
    def server(self) -> tuple[str, int | None]:
        """Server information"""
        return self.asgi_scope["server"]

    @property
    def client(self) -> tuple[str, int] | None:
        """Client information"""
        return self.asgi_scope["client"]

    @property
    def scheme(self) -> str:
        """URL scheme"""
        return self.asgi_scope["scheme"]

    @property
    def root_path(self) -> str:
        """Root path"""
        return self.asgi_scope["root_path"]

    @property
    def path(self) -> str:
        """Request path"""
        return self.asgi_scope["path"]

    @property
    def raw_path(self) -> str | None:
        """Raw request path"""
        return self.asgi_scope["raw_path"]

    @property
    def headers(self) -> Headers:
        """Request headers"""

        if HEADERS not in self.asgi_scope[SCOPE_ASGIKIT][REQUEST]:
            self.asgi_scope[SCOPE_ASGIKIT][REQUEST][HEADERS] = Headers(
                self.asgi_scope["headers"]
            )
        return self.asgi_scope[SCOPE_ASGIKIT][REQUEST][HEADERS]

    @property
    def raw_query(self) -> str:
        """Raw query string"""
        return unquote_plus(self.asgi_scope["query_string"].decode("ascii"))

    @property
    def query(self) -> MultiValueDict[str]:
        """Parsed query string"""

        if QUERY not in self.asgi_scope[SCOPE_ASGIKIT][REQUEST]:
            query_string = self.raw_query
            parsed_query = MultiValueDict(
                parse_qsl(query_string, keep_blank_values=True)
            )
            self.asgi_scope[SCOPE_ASGIKIT][REQUEST][QUERY] = parsed_query
        return self.asgi_scope[SCOPE_ASGIKIT][REQUEST][QUERY]

    @property
    def cookies(self) -> MultiValueDict[str]:
        """Request cookies"""

        if COOKIES not in self.asgi_scope[SCOPE_ASGIKIT][REQUEST]:
            if cookies := self.headers.get("cookie"):
                cookie_value = parse_cookie(cookies)
            else:
                cookie_value = {}
            self.asgi_scope[SCOPE_ASGIKIT][REQUEST][COOKIES] = cookie_value
        return self.asgi_scope[SCOPE_ASGIKIT][REQUEST][COOKIES]

    # Compatibility with asgikit middleware
    @property
    def session(self) -> Any:
        """Get the `session` attribute from the asgi scope

        For compatibility with starlette middleware
        """
        return self.asgi_scope.get("session")

    @property
    def auth(self) -> Any:
        """Get the `auth` attribute from the asgi scope

        For compatibility with starlette middleware
        """
        return self.asgi_scope.get("auth")

    @property
    def user(self) -> Any:
        """Get the `user` attribute from the asgi scope

        For compatibility with starlette middleware
        """
        return self.asgi_scope.get("user")

    @property
    def path_params(self) -> dict[str, Any]:
        """Get the `path_params` attribute from the asgi scope

        For compatibility with starlette middleware
        """
        return self.asgi_scope.get("path_params")

    # ...
