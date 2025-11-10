import pytest

from asgikit.multi_value_dict import MultiValueDict, MutableMultiValueDict


def test_initial_data():
    result = MultiValueDict([("a", 1), ("b", 2)])
    assert result == {"a": [1], "b": [2]}


def test_from_dict():
    d = MutableMultiValueDict.from_dict({"a": [1, 2]})
    assert d == {"a": [1, 2]}


def test_add_single_value():
    d = MutableMultiValueDict()

    d.add("a", 1)
    assert d == {"a": [1]}

    d.add("a", 2)
    assert d == {"a": [1, 2]}


def test_set_single_value():
    d = MutableMultiValueDict()

    d.set("a", 1)
    assert d == {"a": [1]}

    d.set("a", 2)
    assert d == {"a": [2]}


def test_add_multiple_values():
    d = MutableMultiValueDict()

    d.add("a", 1, 2)
    assert d == {"a": [1, 2]}

    d.add("a", 3, 4)
    assert d == {"a": [1, 2, 3, 4]}


def test_set_multiple_values():
    d = MutableMultiValueDict()

    d.set("a", 1, 2)
    assert d == {"a": [1, 2]}

    d.set("a", 3, 4)
    assert d == {"a": [3, 4]}


def test_setitem_not_list_should_fail():
    d = MutableMultiValueDict()

    with pytest.raises(AssertionError):
        d["a"] = 1


def test_setitem():
    d = MutableMultiValueDict()

    d["a"] = [1, 2]
    assert d == {"a": [1, 2]}

    d["a"] = [3, 4]
    assert d == {"a": [3, 4]}


def test_get_first():
    d = MutableMultiValueDict.from_dict({"a": [1, 2]})
    assert d.get_first("a") == 1


def test_get_all():
    d = MutableMultiValueDict.from_dict({"a": [1, 2]})
    assert d.get("a") == [1, 2]


def test_getitem():
    d = MutableMultiValueDict.from_dict({"a": [1, 2]})
    assert d["a"] == [1, 2]


def test_delitem():
    d = MutableMultiValueDict.from_dict({"a": [1, 2]})
    del d["a"]
    assert d == {}


def test_mapping_methods():
    d = MutableMultiValueDict.from_dict({"a": 1, "b": [2, 3]})
    assert list(d.keys()) == ["a", "b"]
    assert list(d.values()) == [[1], [2, 3]]
    assert list(d.items()) == [("a", [1]), ("b", [2, 3])]
    assert len(d) == 2
    assert list(iter(d)) == [("a", 1), ("b", 2), ("b", 3)]
    assert "a" in d
