import pytest
from pollywog.conversion.sklearn import convert_tree, convert_linear_model
from pollywog.core import Number, Category
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.linear_model import LinearRegression
import numpy as np


def make_regressor():
    X = np.array([[0, 0], [1, 1], [2, 2]])
    y = np.array([0, 1, 2])
    return DecisionTreeRegressor().fit(X, y)


def make_linear():
    X = np.array([[0, 0], [1, 0], [0, 1]])
    y = np.array([1, 3, 1])
    lm = LinearRegression().fit(X, y)
    lm.coef_ = np.array([2.0, 0.0])
    lm.intercept_ = 1.0
    return lm


class DummyTree:
    class tree_:
        feature = [0, -2, -2]
        threshold = [1.5, 0, 0]
        children_left = [1, -1, -1]
        children_right = [2, -1, -1]
        value = [[[0]], [[1]], [[2]]]

    class _tree:
        class Dummy:
            pass


def test_convert_tree_regressor():
    tree = make_regressor()
    result = convert_tree(tree, ["x1", "x2"], "target")
    assert isinstance(result, Number)
    assert result.name == "target"
    assert "Converted from DecisionTreeRegressor" in result.comment_equation


def test_convert_tree_classifier():
    X = np.array([[0, 0], [1, 1], [2, 2]])
    y = np.array([0, 1, 2])
    tree = DecisionTreeClassifier().fit(X, y)
    result = convert_tree(tree, ["x1", "x2"], "target")
    assert isinstance(result, Category)
    assert result.name == "target"
    assert "Converted from DecisionTreeClassifier" in result.comment_equation


def test_convert_tree_invalid():
    class Dummy:
        pass

    dummy = Dummy()
    dummy.__class__ = type("UnknownTree", (), {})
    with pytest.raises(Exception):
        convert_tree(dummy, ["x1"], "target")


def test_convert_linear_model():
    lm = make_linear()
    result = convert_linear_model(lm, ["x1", "x2"], "target")
    assert isinstance(result, Number)
    assert result.name == "target"
    assert "Converted from LinearRegression" in result.comment_equation
    assert "1.000000" in result.expression[0]
    assert "2.000000 * [x1]" in result.expression[0]


def test_convert_tree_with_complex_structure():
    """Test converting a tree with more complex structure."""
    # Create a tree with more splits
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1], [2, 2]])
    y = np.array([0, 1, 1, 0, 2])
    tree = DecisionTreeRegressor(max_depth=2).fit(X, y)

    result = convert_tree(tree, ["feature1", "feature2"], "output")
    assert isinstance(result, Number)
    assert result.name == "output"
    assert "Converted from DecisionTreeRegressor" in result.comment_equation


def test_convert_tree_classifier_multiclass():
    """Test converting a multi-class classifier."""
    X = np.array([[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]])
    y = np.array([0, 1, 2, 0, 1])  # 3 classes
    tree = DecisionTreeClassifier().fit(X, y)

    result = convert_tree(tree, ["x1", "x2"], "class_output")
    assert isinstance(result, Category)
    assert result.name == "class_output"


def test_convert_linear_with_single_feature():
    """Test converting linear model with single feature."""
    X = np.array([[1], [2], [3]])
    y = np.array([2, 4, 6])
    lm = LinearRegression().fit(X, y)

    result = convert_linear_model(lm, ["x"], "y_pred")
    assert isinstance(result, Number)
    assert result.name == "y_pred"
    assert "[x]" in result.expression[0]


def test_convert_linear_with_zero_coefficients():
    """Test linear model where some coefficients are zero."""
    lm = make_linear()
    # Second coefficient is already 0 in make_linear
    result = convert_linear_model(lm, ["x1", "x2"], "target")

    # Should handle zero coefficient gracefully
    assert isinstance(result, Number)
    # x2 coefficient is 0, so it might be excluded or included as 0 * [x2]
    assert "[x1]" in result.expression[0]
