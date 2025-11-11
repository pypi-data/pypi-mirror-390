import pollywog.display
import pytest


# Dummy CalcSet and Item for testing
class DummyItem:
    def __init__(self, name, typ, calc_type=None):
        self.name = name
        self.item_type = typ
        self.calculation_type = calc_type

    def to_dict(self):
        d = {"name": self.name, "type": self.item_type}
        if self.calculation_type:
            d["calculation_type"] = self.calculation_type
        return d


class DummyCalcSet:
    def __init__(self, items):
        self.items = items


# Test set_theme and theme switching
def test_set_theme():
    pollywog.display.set_theme("dark")
    assert pollywog.display._DISPLAY_THEME == "dark"
    pollywog.display.set_theme("light")
    assert pollywog.display._DISPLAY_THEME == "light"
    with pytest.raises(ValueError):
        pollywog.display.set_theme("unknown")


# Test display_calcset does not error and produces HTML
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_display_calcset_html(theme):
    pollywog.display.set_theme(theme)
    items = [
        DummyItem("A", "variable"),
        DummyItem("B", "calculation", "number"),
        DummyItem("C", "calculation", "string"),
        DummyItem("D", "filter"),
    ]
    calcset = DummyCalcSet(items)
    # Should not raise
    pollywog.display.display_calcset(calcset)
    # Should produce HTML output (not None)
    # (We can't check the actual rendering, but can check no error)


# Optionally, test that the HTML contains expected labels
@pytest.mark.parametrize("theme,label", [("light", "number"), ("dark", "string")])
def test_display_calcset_label(theme, label):
    pollywog.display.set_theme(theme)
    items = [DummyItem("B", "calculation", label)]
    calcset = DummyCalcSet(items)
    # Monkeypatch display to capture HTML
    import IPython.display

    captured = {}

    def fake_display(obj):
        captured["html"] = obj.data if hasattr(obj, "data") else str(obj)

    orig_display = IPython.display.display
    IPython.display.display = fake_display
    pollywog.display.display_calcset(calcset)
    IPython.display.display = orig_display
    assert label in captured["html"]


# Test display_item function
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_display_item_html(theme):
    pollywog.display.set_theme(theme)
    item = DummyItem("test_var", "variable")
    # Should not raise
    pollywog.display.display_item(item)
    # Check it returns HTML when display_output=False
    html = pollywog.display.display_item(item, display_output=False)
    assert isinstance(html, str)
    assert "test_var" in html
    assert "variable" in html
