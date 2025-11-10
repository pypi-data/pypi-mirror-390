import pytest

from asgikit.headers import Headers, MutableHeaders


@pytest.mark.parametrize(
    "raw,parsed",
    [
        ([(b"a", b"1"), (b"b", b"2")], {"a": ["1"], "b": ["2"]}),
        ([(b"a", b"1, 2"), (b"b", b"3, 4")], {"a": ["1, 2"], "b": ["3, 4"]}),
        (
            [(b"a", b"1"), (b"a", b"2"), (b"b", b"3"), (b"b", b"4")],
            {"a": ["1", "2"], "b": ["3", "4"]},
        ),
        ([], {}),
    ],
)
def test_parse(raw, parsed):
    result = Headers(raw)
    assert result == parsed


def test_from_dict():
    h = Headers.from_dict({"a": ["1", "2"]})
    assert h == {"a": ["1", "2"]}


@pytest.mark.parametrize(
    "parsed,encoded",
    [
        ({"a": ["1"], "b": ["2"]}, [(b"a", b"1"), (b"b", b"2")]),
        (
            {"a": ["1", "2"], "b": ["3", "4"]},
            [(b"a", b"1, 2"), (b"b", b"3, 4")],
        ),
        ({}, []),
    ],
)
def test_encode(parsed, encoded):
    headers = MutableHeaders.from_dict(parsed)
    result = list(headers.encode())
    assert result == encoded


@pytest.mark.parametrize(
    "data,expected",
    [
        ({"a": "1", "b": "2"}, {"a": ["1"], "b": ["2"]}),
        ({"a": ["1"], "b": "1"}, {"a": ["1"], "b": ["1"]}),
        ({"a": "1", "b": ["1"]}, {"a": ["1"], "b": ["1"]}),
        ({"a": ["1"], "b": ["1"]}, {"a": ["1"], "b": ["1"]}),
    ],
)
def test_from_dict(data, expected):
    result = Headers.from_dict(data)
    assert result == expected


def test_add_single_value():
    h = MutableHeaders()

    h.add("A", "1")
    assert h == {"a": ["1"]}

    h.add("a", "2")
    assert h == {"a": ["1", "2"]}


def test_set_single_value():
    h = MutableHeaders()

    h.set("A", "1")
    assert h == {"a": ["1"]}

    h.set("a", "2")
    assert h == {"a": ["2"]}


def test_add_multiple_values():
    h = MutableHeaders()

    h.add("A", "1", "2")
    assert h == {"a": ["1", "2"]}

    h.add("a", "3", "4")
    assert h == {"a": ["1", "2", "3", "4"]}


def test_set_multiple_values():
    h = MutableHeaders()

    h.set("A", "1", "2")
    assert h == {"a": ["1", "2"]}

    h.set("a", "3", "4")
    assert h == {"a": ["3", "4"]}


def test_setitem_not_list_should_fail():
    h = MutableHeaders()

    with pytest.raises(AssertionError):
        h["a"] = "1"


def test_setitem():
    h = MutableHeaders()

    h["A"] = ["1", "2"]
    assert h == {"a": ["1", "2"]}

    h["a"] = ["3", "4"]
    assert h == {"a": ["3", "4"]}


def test_get_first():
    h = MutableHeaders.from_dict({"A": ["1", "2"]})
    assert h.get_first("a") == "1"


def test_get_all():
    h = MutableHeaders.from_dict({"A": ["1", "2"]})
    assert h.get("a") == ["1", "2"]


def test_getitem():
    h = MutableHeaders.from_dict({"A": ["1", "2"]})
    assert h["a"] == ["1", "2"]


def test_delitem():
    h = MutableHeaders.from_dict({"A": ["1", "2"]})
    del h["a"]
    assert h == {}


def test_mapping_methods():
    d = MutableHeaders.from_dict({"a": "1", "b": ["2", "3"]})
    assert list(d.keys()) == ["a", "b"]
    assert list(d.values()) == [["1"], ["2", "3"]]
    assert list(d.items()) == [("a", ["1"]), ("b", ["2", "3"])]
    assert len(d) == 2
    assert list(iter(d)) == [("a", "1"), ("b", "2"), ("b", "3")]
    assert "a" in d
