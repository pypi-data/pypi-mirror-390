import pytest
from pollywog.core import CalcSet, Variable, Number, If, IfRow
from pollywog.run import run_calcset


def test_import_run():
    # Just test that run.py imports without error
    assert True


def test_run_calcset_with_dict():
    a = Variable(name="a", expression=[""])
    b = Number(name="b", expression=["[a] + 1"])
    c = Number(name="c", expression=["[b] * 2"])
    cs = CalcSet([a, b, c])
    inputs = {"a": 3}
    results = run_calcset(cs, inputs=inputs)
    assert "a" not in results  # Variable should not be in output by default
    assert results["b"] == 4
    assert results["c"] == 8
    # Debug mode: output_variables=True
    debug_results = run_calcset(cs, inputs=inputs, output_variables=True)
    assert debug_results["a"] == 3
    assert debug_results["b"] == 4
    assert debug_results["c"] == 8


def test_run_calcset_with_if():
    a = Variable(name="a", expression=[""])
    ifrow1 = IfRow(condition=["[a] > 0"], value=["1"])
    ifrow2 = IfRow(condition=["[a] <= 0"], value=["-1"])
    ifexpr = If(rows=[ifrow1, ifrow2], otherwise=["0"])
    b = Number(name="b", expression=[ifexpr])
    cs = CalcSet([a, b])
    results = run_calcset(cs, inputs={"a": 2})
    assert "a" not in results
    assert results["b"] == 1
    results = run_calcset(cs, inputs={"a": -2})
    assert results["b"] == -1
    results = run_calcset(cs, inputs={"a": 0})
    assert results["b"] == -1
    # Debug mode
    debug_results = run_calcset(cs, inputs={"a": 2}, output_variables=True)
    assert debug_results["a"] == 2
    assert debug_results["b"] == 1


def test_run_calcset_with_dataframe():
    import pandas as pd

    a = Variable(name="a", expression=[""])
    b = Number(name="b", expression=["[a] + 1"])
    cs = CalcSet([a, b])
    df = pd.DataFrame({"a": [1, 2, 3]})
    result_df = run_calcset(cs, dataframe=df)
    assert list(result_df["b"]) == [2, 3, 4]
    assert "a" not in result_df.columns  # Variable column should be dropped
    # Debug mode
    debug_df = run_calcset(cs, dataframe=df, output_variables=True)
    assert "a" in debug_df.columns
    assert list(debug_df["a"]) == [1, 2, 3]


def test_pw_accessor():
    import pandas as pd

    b = Number(name="b", expression=["[a] + 1"])
    cs = CalcSet([b])
    df = pd.DataFrame({"a": [10, 20]})
    result_df = df.pw.run(cs)
    assert list(result_df["b"]) == [11, 21]


def test_run_with_math_functions():
    """Test that Leapfrog-like math functions work correctly."""
    import math

    # Test log function
    a = Variable(name="a", expression=[""])
    b = Number(name="log10_result", expression=["log([a], 10)"])
    c = Number(name="ln_result", expression=["ln([a])"])
    d = Number(name="exp_result", expression=["exp([a])"])
    e = Number(name="sqrt_result", expression=["sqrt([a])"])

    cs = CalcSet([a, b, c, d, e])
    results = run_calcset(cs, inputs={"a": 100})

    assert abs(results["log10_result"] - 2.0) < 0.001
    assert abs(results["ln_result"] - math.log(100)) < 0.001
    assert abs(results["exp_result"] - math.exp(100)) < 0.001
    assert abs(results["sqrt_result"] - 10.0) < 0.001


def test_run_with_trig_functions():
    """Test trigonometric functions."""
    import math

    a = Variable(name="angle", expression=[""])
    b = Number(name="sin_result", expression=["sin([angle])"])
    c = Number(name="cos_result", expression=["cos([angle])"])
    d = Number(name="tan_result", expression=["tan([angle])"])

    cs = CalcSet([a, b, c, d])
    results = run_calcset(cs, inputs={"angle": math.pi / 4})

    assert abs(results["sin_result"] - math.sqrt(2) / 2) < 0.001
    assert abs(results["cos_result"] - math.sqrt(2) / 2) < 0.001
    assert abs(results["tan_result"] - 1.0) < 0.001


def test_run_with_inverse_trig_functions():
    """Test inverse trigonometric functions."""
    import math

    a = Variable(name="x", expression=[""])
    b = Number(name="asin_result", expression=["asin([x])"])
    c = Number(name="acos_result", expression=["acos([x])"])
    d = Number(name="atan_result", expression=["atan([x])"])

    cs = CalcSet([a, b, c, d])
    results = run_calcset(cs, inputs={"x": 0.5})

    assert abs(results["asin_result"] - math.asin(0.5)) < 0.001
    assert abs(results["acos_result"] - math.acos(0.5)) < 0.001
    assert abs(results["atan_result"] - math.atan(0.5)) < 0.001


def test_run_with_trig_functions():
    """Test trigonometric functions."""
    import math

    a = Variable(name="angle", expression=[""])
    b = Number(name="sin_result", expression=["sin([angle])"])
    c = Number(name="cos_result", expression=["cos([angle])"])
    d = Number(name="tan_result", expression=["tan([angle])"])

    cs = CalcSet([a, b, c, d])
    results = run_calcset(cs, inputs={"angle": math.pi / 4})

    assert abs(results["sin_result"] - math.sqrt(2) / 2) < 0.001
    assert abs(results["cos_result"] - math.sqrt(2) / 2) < 0.001
    assert abs(results["tan_result"] - 1.0) < 0.001


def test_run_with_inverse_trig_functions():
    """Test inverse trigonometric functions."""
    import math

    a = Variable(name="x", expression=[""])
    b = Number(name="asin_result", expression=["asin([x])"])
    c = Number(name="acos_result", expression=["acos([x])"])
    d = Number(name="atan_result", expression=["atan([x])"])

    cs = CalcSet([a, b, c, d])
    results = run_calcset(cs, inputs={"x": 0.5})

    assert abs(results["asin_result"] - math.asin(0.5)) < 0.001
    assert abs(results["acos_result"] - math.acos(0.5)) < 0.001
    assert abs(results["atan_result"] - math.atan(0.5)) < 0.001


def test_run_with_string_functions():
    """Test string manipulation functions."""
    a = Variable(name="text", expression=[""])
    b = Number(name="starts", expression=["startswith([text], 'Hello')"])
    c = Number(name="ends", expression=["endswith([text], 'world')"])
    d = Number(name="has", expression=["contains([text], 'beautiful')"])

    cs = CalcSet([a, b, c, d])

    # Test with matching string
    results = run_calcset(cs, inputs={"text": "Hello beautiful world"})
    assert results["starts"] is True
    assert results["ends"] is True
    assert results["has"] is True

    # Test with non-matching string
    results = run_calcset(cs, inputs={"text": "Goodbye cruel world"})
    assert results["starts"] is False
    assert results["ends"] is True
    assert results["has"] is False


def test_run_with_concat():
    """Test string concatenation function."""
    a = Variable(name="first", expression=[""])
    b = Variable(name="last", expression=[""])
    c = Number(name="full_name", expression=["concat([first], ' ', [last])"])

    cs = CalcSet([a, b, c])
    results = run_calcset(cs, inputs={"first": "John", "last": "Doe"})

    assert results["full_name"] == "John Doe"


def test_run_with_error_handling():
    """Test that errors in expressions are handled gracefully."""
    a = Variable(name="x", expression=[""])
    # Division by zero should return None
    b = Number(name="div_zero", expression=["[x] / 0"])
    # Undefined variable should return None
    c = Number(name="undefined", expression=["[y] + 1"])

    cs = CalcSet([a, b, c])
    results = run_calcset(cs, inputs={"x": 5})

    # Errors should result in None values
    assert results["div_zero"] is None
    assert results["undefined"] is None


def test_run_with_complex_if():
    """Test complex If structures with multiple conditions."""
    a = Variable(name="grade", expression=[""])
    ifrow1 = IfRow(condition=["[grade] >= 90"], value=["'A'"])
    ifrow2 = IfRow(condition=["[grade] >= 80"], value=["'B'"])
    ifrow3 = IfRow(condition=["[grade] >= 70"], value=["'C'"])
    ifexpr = If(rows=[ifrow1, ifrow2, ifrow3], otherwise=["'F'"])
    b = Number(name="letter_grade", expression=[ifexpr])

    cs = CalcSet([a, b])

    # Test different grade ranges
    assert run_calcset(cs, inputs={"grade": 95})["letter_grade"] == "A"
    assert run_calcset(cs, inputs={"grade": 85})["letter_grade"] == "B"
    assert run_calcset(cs, inputs={"grade": 75})["letter_grade"] == "C"
    assert run_calcset(cs, inputs={"grade": 65})["letter_grade"] == "F"


def test_run_with_nested_if():
    """Test nested If structures."""
    a = Variable(name="x", expression=[""])
    # Inner If
    inner_ifrow = IfRow(condition=["[x] > 0"], value=["1"])
    inner_if = If(rows=[inner_ifrow], otherwise=["-1"])
    # Outer If
    outer_ifrow = IfRow(condition=["[x] != 0"], value=[inner_if])
    outer_if = If(rows=[outer_ifrow], otherwise=["0"])
    b = Number(name="result", expression=[outer_if])

    cs = CalcSet([a, b])

    assert run_calcset(cs, inputs={"x": 5})["result"] == 1
    assert run_calcset(cs, inputs={"x": -5})["result"] == -1
    assert run_calcset(cs, inputs={"x": 0})["result"] == 0


def test_run_with_clamp():
    """Test clamp function with fixed infinite recursion bug."""
    a = Variable(name="x", expression=[""])
    b = Number(name="clamped", expression=["clamp([x], 0, 10)"])
    c = Number(name="clamped_lower", expression=["clamp([x], 5)"])

    cs = CalcSet([a, b, c])

    # Test value within bounds
    results = run_calcset(cs, inputs={"x": 5})
    assert results["clamped"] == 5
    assert results["clamped_lower"] == 5

    # Test value below lower bound
    results = run_calcset(cs, inputs={"x": -5})
    assert results["clamped"] == 0
    assert results["clamped_lower"] == 5

    # Test value above upper bound
    results = run_calcset(cs, inputs={"x": 15})
    assert results["clamped"] == 10
    assert results["clamped_lower"] == 15


def test_run_with_min_max():
    """Test min and max functions with fixed infinite recursion bug."""
    a = Variable(name="x", expression=[""])
    b = Variable(name="y", expression=[""])
    c = Number(name="min_result", expression=["min([x], [y])"])
    d = Number(name="max_result", expression=["max([x], [y])"])

    cs = CalcSet([a, b, c, d])
    results = run_calcset(cs, inputs={"x": 5, "y": 10})

    assert results["min_result"] == 5
    assert results["max_result"] == 10

    # Test with negative values
    results = run_calcset(cs, inputs={"x": -3, "y": -7})
    assert results["min_result"] == -7
    assert results["max_result"] == -3


def test_run_with_roundsf():
    """Test roundsf (round to significant figures) function with fixed bug."""
    a = Variable(name="x", expression=[""])
    b = Number(name="rounded_sf", expression=["roundsf([x], 3)"])

    cs = CalcSet([a, b])

    # Test various roundsf cases
    results = run_calcset(cs, inputs={"x": 123.456})
    assert results["rounded_sf"] == 123

    results = run_calcset(cs, inputs={"x": 0.001234})
    assert results["rounded_sf"] == 0.00123


def test_run_with_is_normal():
    """Test is_normal function for detecting valid numbers."""
    a = Variable(name="x", expression=[""])
    b = Number(name="is_valid", expression=["is_normal([x])"])

    cs = CalcSet([a, b])

    # Test normal number
    results = run_calcset(cs, inputs={"x": 5.0})
    assert results["is_valid"] is True

    # Test None value
    results = run_calcset(cs, inputs={"x": None})
    assert results["is_valid"] is False

    # Test with zero (should be normal)
    results = run_calcset(cs, inputs={"x": 0})
    assert results["is_valid"] is True

    # Test with negative number
    results = run_calcset(cs, inputs={"x": -123.456})
    assert results["is_valid"] is True


def test_run_with_abs():
    """Test abs function with fixed infinite recursion bug."""
    a = Variable(name="x", expression=[""])
    b = Number(name="abs_result", expression=["abs([x])"])

    cs = CalcSet([a, b])

    # Test positive number
    results = run_calcset(cs, inputs={"x": 5})
    assert results["abs_result"] == 5

    # Test negative number
    results = run_calcset(cs, inputs={"x": -5})
    assert results["abs_result"] == 5

    # Test zero
    results = run_calcset(cs, inputs={"x": 0})
    assert results["abs_result"] == 0

    # Test decimal
    results = run_calcset(cs, inputs={"x": -3.14})
    assert abs(results["abs_result"] - 3.14) < 0.001
