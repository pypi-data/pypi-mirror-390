from collections.abc import Iterable
from typing import Self

from asgikit._constants import HEADER_ENCODING
from asgikit.multi_value_dict import MultiValueDict, MutableMultiValueDict


class Headers(MultiValueDict[str]):
    """Immutable headers backed by multivalue dict"""

    def __init__(self, data: Iterable[tuple[bytes, bytes]] = None):
        if not data:
            super().__init__()
            return

        super().__init__(
            (key.decode(HEADER_ENCODING).lower(), value.decode(HEADER_ENCODING))
            for key, value in data
        )

    @classmethod
    def from_dict(cls, data: dict[str, list[str]]) -> Self:
        instance = cls()
        instance._data = {
            key.lower(): value if isinstance(value, list) else [value]
            for key, value in data.items()
        }

        return instance

    def get_first(self, key: str, default: str = None) -> str | None:
        return super().get_first(key.lower(), default)

    def get(self, key: str, default: list[str] = None) -> list[str] | None:
        return super().get(key.lower(), default)

    def __getitem__(self, key: str) -> list[str]:
        return super().__getitem__(key.lower())

    def __contains__(self, key: str) -> bool:
        return super().__contains__(key.lower())


class MutableHeaders(MutableMultiValueDict[str], Headers):
    def __init__(self, data=None):
        super(MutableMultiValueDict, self).__init__(data)

    def add(self, key: str, *args: str):
        super().add(key.lower(), *args)

    def set(self, key: str, *args: str):
        super().set(key.lower(), *args)

    def encode(self) -> Iterable[tuple[bytes, bytes]]:
        for name, value in self.items():
            encoded_name = name.encode(HEADER_ENCODING)
            encoded_value = ", ".join(value).encode(HEADER_ENCODING)
            yield encoded_name, encoded_value

    def __setitem__(self, key: str, value: list[str]):
        super().__setitem__(key.lower(), value)

    def __delitem__(self, key: str):
        super().__delitem__(key.lower())
