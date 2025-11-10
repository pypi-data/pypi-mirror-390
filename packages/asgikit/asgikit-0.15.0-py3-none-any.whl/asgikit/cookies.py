import sys
from collections.abc import Iterable
from http.cookies import SimpleCookie
from typing import Literal, TypeAlias

from asgikit._constants import HEADER_ENCODING

__all__ = ("Cookies", "SameSitePolicy")

SameSitePolicy: TypeAlias = Literal["strict", "lax", "none"]


class Cookies:
    """Cookies to be sent in the response"""

    __slots__ = ("_cookie",)

    def __init__(self):
        self._cookie = SimpleCookie()

    # pylint: disable=too-many-arguments
    def set(
        self,
        name: str,
        value: str,
        *,
        expires: int = None,
        domain: str = None,
        path: str = None,
        max_age: int = None,
        secure: bool = False,
        httponly: bool = True,
        samesite: SameSitePolicy = "lax",
        partitioned: bool = False,
    ):
        """Add a cookie to the response"""

        self._cookie[name] = value
        if expires is not None:
            self._cookie[name]["expires"] = expires
        if domain is not None:
            self._cookie[name]["domain"] = domain
        if path is not None:
            self._cookie[name]["path"] = path
        if max_age is not None:
            self._cookie[name]["max-age"] = max_age

        self._cookie[name]["secure"] = secure
        self._cookie[name]["httponly"] = httponly
        self._cookie[name]["samesite"] = samesite

        if partitioned:
            if sys.version_info < (3, 14):
                raise NotImplementedError(
                    "Partitioned cookies are only supported in Python >= 3.14."
                )
            self._cookie[name]["partitioned"] = True

    def delete(
        self,
        name: str,
        *,
        domain: str = None,
        path: str = None,
        secure: bool = False,
        httponly: bool = True,
        samesite: SameSitePolicy = "lax",
    ):
        self.set(
            name,
            "",
            expires=0,
            max_age=0,
            domain=domain,
            path=path,
            secure=secure,
            httponly=httponly,
            samesite=samesite,
        )

    def encode(self) -> Iterable[tuple[bytes, bytes]]:
        for c in self._cookie.values():
            yield b"Set-Cookie", c.output(header="").strip().encode(HEADER_ENCODING)

    def __eq__(self, other):
        return isinstance(other, Cookies) and self._cookie == other._cookie

    def __hash__(self):
        return hash(self._cookie)

    def __getitem__(self, item):
        return self._cookie[item]
