from pollywog.utils import ensure_list, ensure_str_list, to_dict


class Dummy:
    def to_dict(self):
        return {"dummy": True}


def test_ensure_list():
    assert ensure_list(1) == [1]
    assert ensure_list([1, 2]) == [1, 2]


def test_ensure_str_list():
    assert ensure_str_list("foo") == ["foo"]
    assert ensure_str_list(["foo"]) == ["foo"]
    assert ensure_str_list([1]) == ["", 1, ""]
    assert ensure_str_list(["foo", 1]) == ["foo", 1, ""]
    assert ensure_str_list(["foo", "bar"]) == ["foo", "bar"]


def test_to_dict():
    d = Dummy()
    assert to_dict(d) == [{"dummy": True}]
    assert to_dict([d, d]) == [{"dummy": True}, {"dummy": True}]
    assert to_dict(["a", "b"]) == ["a", "b"]
    assert to_dict(["a", d]) == ["a", {"dummy": True}]
    # guard_strings True
    assert to_dict([d], guard_strings=True) == ["", {"dummy": True}, ""]
    assert to_dict(["a", d], guard_strings=True) == ["a", {"dummy": True}, ""]
    assert to_dict([d, "a"], guard_strings=True) == ["", {"dummy": True}, "a"]
    assert to_dict(["a", "b"], guard_strings=True) == ["a", "b"]
