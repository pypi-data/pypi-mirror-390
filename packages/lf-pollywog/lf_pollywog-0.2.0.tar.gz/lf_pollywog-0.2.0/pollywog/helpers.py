from .core import If, IfRow, Number, Category
from .utils import ensure_variables, ensure_brackets


def Sum(variables, name=None, comment=None, ignore_functions=True):
    """
    Create a sum expression or a Number representing the sum of the given variables.

    Args:
        variables (list of str): Variable names (as strings) to sum, e.g. ["Au", "Ag"].
        name (str, optional): Name for the output variable. If provided, returns a Number; if None, returns the sum expression as a string.
        comment (str, optional): Optional comment for the calculation. Used only if name is provided.
        ignore_functions (bool): If True, strings that appear to be function
            calls (e.g., "max([Au], [Ag])") are not wrapped in brackets. Defaults to True.

    Returns:
        Number or str: If name is provided, returns a pollywog Number representing the sum calculation. If name is None, returns the sum expression as a string.

    Raises:
        ValueError: If variables is empty.

    Example:
        >>> from pollywog.helpers import Sum
        >>> Sum(["Au", "Ag"], name="total_precious")
        >>> Sum(["Au", "Ag", "Cu"])
    """
    if not variables:
        raise ValueError("At least one variable must be provided.")
    variables = ensure_variables(variables, ignore_functions=ignore_functions)
    expr = f"({' + '.join(f'{v}' for v in variables)})"
    if name is None:
        return expr
    return Number(
        name, [expr], comment_equation=comment or f"Sum of {', '.join(variables)}"
    )


def WeightedSum(variables, weights, name=None, comment=None, ignore_functions=True):
    """
    Create a weighted sum expression or a Number representing the weighted sum of the given variables.

    Args:
        variables (list of str): Variable names (as strings) to sum, e.g. ["Au", "Ag"].
        weights (list of float or str): Corresponding weights for each variable. Can be constants or variable names.
        name (str, optional): Name for the output variable. If provided, returns a Number; if None, returns the weighted sum expression as a string.
        comment (str, optional): Optional comment for the calculation. Used only if name is provided.
        ignore_functions (bool): If True, strings that appear to be function
            calls (e.g., "max([Au], [Ag])") are not wrapped in brackets.
            Defaults to True.

    Returns:
        Number or str: If name is provided, returns a pollywog Number representing the weighted sum calculation. If name is None, returns the weighted sum expression as a string.

    Raises:
        ValueError: If variables and weights are empty or have different lengths.
    """
    if not variables or not weights or len(variables) != len(weights):
        raise ValueError("variables and weights must be non-empty and of equal length.")
    weights = ensure_variables(weights, ignore_functions=ignore_functions)
    variables = ensure_variables(variables, ignore_functions=ignore_functions)
    weighted_terms = [f"{v} * {w}" for v, w in zip(variables, weights)]
    expr = f"({' + '.join(weighted_terms)})"
    if name is None:
        return expr
    return Number(
        name,
        [expr],
        comment_equation=comment
        or f"Weighted sum of {', '.join(variables)} with weights {weights}",
    )


def Product(variables, name=None, comment=None, ignore_functions=True):
    """
    Create a product expression or a Number representing the product of the given variables.

    Args:
        variables (list of str): Variable names (as strings) to multiply, e.g. ["Au", "Ag"].
        name (str, optional): Name for the output variable. If provided, returns a Number; if None, returns the product expression as a string.
        comment (str, optional): Optional comment for the calculation. Used only if name is provided.
        ignore_functions (bool): If True, strings that appear to be function
            calls (e.g., "max([Au], [Ag])") are not wrapped in brackets. Defaults to True.

    Returns:
        Number or str: If name is provided, returns a pollywog Number representing the product calculation. If name is None, returns the product expression as a string.

    Raises:
        ValueError: If variables is empty.

    Example:
        >>> from pollywog.helpers import Product
        >>> Product(["grade", "tonnage"], name="metal_content")
        >>> Product(["Au", "recovery", "price"])
    """
    if not variables:
        raise ValueError("At least one variable must be provided.")
    variables = ensure_variables(variables, ignore_functions=ignore_functions)
    expr = f"({' * '.join(f'{v}' for v in variables)})"
    if name is None:
        return expr
    return Number(
        name, [expr], comment_equation=comment or f"Product of {', '.join(variables)}"
    )


def Normalize(variable, min_value, max_value, name=None, comment=None, ignore_functions=True):
    """
    Create a normalization expression or a Number that normalizes a variable to the range [0, 1].

    Args:
        variable (str): Variable name to normalize.
        min_value (float): Minimum value for normalization (maps to 0).
        max_value (float): Maximum value for normalization (maps to 1).
        name (str, optional): Name for the output variable. If provided, returns a Number; if None, returns the normalization expression as a string.
        comment (str, optional): Optional comment for the calculation. Used only if name is provided.
        ignore_functions (bool): If True, strings that appear to be function
            calls (e.g., "max([Au], [Ag])") are not wrapped in brackets. Defaults to True.

    Returns:
        Number or str: If name is provided, returns a pollywog Number representing the normalization calculation. If name is None, returns the normalization expression as a string.

    Example:
        >>> from pollywog.helpers import Normalize
        >>> Normalize("Au", 0, 10, name="Au_normalized")
        >>> Normalize("porosity", 0.1, 0.3)
    """
    variable = ensure_brackets(variable, ignore_functions=ignore_functions)
    expr = f"({variable} - {min_value}) / ({max_value} - {min_value})"
    if name is None:
        return expr
    return Number(
        name,
        [expr],
        comment_equation=comment
        or f"Normalize {variable} to [0, 1] using min={min_value}, max={max_value}",
    )


def Average(variables, name=None, comment=None, ignore_functions=True):
    """
    Create an average expression or a Number representing the arithmetic mean of the given variables.

    Args:
        variables (list of str): Variable names (as strings) to average, e.g. ["Au", "Ag"].
        name (str, optional): Name for the output variable. If provided, returns a Number; if None, returns the average expression as a string.
        comment (str, optional): Optional comment for the calculation. Used only if name is provided.
        ignore_functions (bool): If True, strings that appear to be function
            calls (e.g., "max([Au], [Ag])") are not wrapped in brackets. Defaults to True.

    Returns:
        Number or str: If name is provided, returns a pollywog Number representing the average calculation. If name is None, returns the average expression as a string.

    Raises:
        ValueError: If variables is empty.

    Example:
        >>> from pollywog.helpers import Average
        >>> Average(["Au_est1", "Au_est2", "Au_est3"], name="Au_avg")
        >>> Average(["density_dry", "density_wet"])
    """
    if not variables:
        raise ValueError("At least one variable must be provided.")
    variables = ensure_variables(variables, ignore_functions=ignore_functions)
    expr = f"({' + '.join(f'{v}' for v in variables)}) / {len(variables)}"
    if name is None:
        return expr
    return Number(
        name, [expr], comment_equation=comment or f"Average of {', '.join(variables)}"
    )


def WeightedAverage(variables, weights, name=None, comment=None, ignore_functions=True):
    """
    Create a weighted average expression or a Number representing the weighted average of variables.

    Args:
        variables (list of str): Variable names to average, e.g. ["Au", "Ag", "Cu"].
        weights (list of float or str): Corresponding weights for each variable. Can be constants or variable names.
        name (str, optional): Name for the output variable. If provided, returns a Number; if None, returns the weighted average expression as a string.
        comment (str, optional): Optional comment for the calculation. Used only if name is provided.
        ignore_functions (bool): If True, strings that appear to be function
            calls (e.g., "max([Au], [Ag])") are not wrapped in brackets.
            Defaults to True.

    Returns:
        Number or str: If name is provided, returns a pollywog Number representing the weighted average calculation. If name is None, returns the weighted average expression as a string.

    Raises:
        ValueError: If variables and weights are empty or have different lengths.

    Example:
        >>> from pollywog.helpers import WeightedAverage
        >>> WeightedAverage(["Au_oxide", "Au_sulfide"], [0.7, 0.3], name="Au_composite")
        >>> WeightedAverage(["est1", "est2"], ["weight1", "weight2"])
    """
    if not variables or not weights or len(variables) != len(weights):
        raise ValueError("variables and weights must be non-empty and of equal length.")
    weights = ensure_variables(weights, ignore_functions=ignore_functions)
    variables = ensure_variables(variables, ignore_functions=ignore_functions)
    sum_weights = " + ".join(weights)
    weighted_terms = [f"{v} * {w}" for v, w in zip(variables, weights)]
    expr = f"({' + '.join(weighted_terms)}) / ({sum_weights})"
    if name is None:
        return expr
    return Number(
        name,
        [expr],
        comment_equation=comment
        or f"Weighted average of {', '.join(variables)} with weights {weights}",
    )


def Scale(variable, factor, name=None, comment=None):
    """
    Create a scaling expression or a Number that multiplies a variable by a scaling factor.

    Args:
        variable (str): Variable name to scale.
        factor (float or str): Scaling factor. Can be a numeric constant or another variable name.
        name (str, optional): Name for the output variable. If provided, returns a Number; if None, returns the scaling expression as a string.
        comment (str, optional): Optional comment for the calculation. Used only if name is provided.

    Returns:
        Number or str: If name is provided, returns a pollywog Number representing the scaled variable. If name is None, returns the scaling expression as a string.

    Example:
        >>> from pollywog.helpers import Scale
        >>> Scale("Au_ppm", 0.001, name="Au_percent")
        >>> Scale("tonnes", 2204.62)
    """
    factor_expr = f"[{factor}]" if isinstance(factor, str) else str(factor)
    expr = f"[{variable}] * {factor_expr}"
    if name is None:
        return expr
    return Number(
        name, [expr], comment_equation=comment or f"Scale {variable} by {factor}"
    )


def CategoryFromThresholds(variable, thresholds, categories, name=None, comment=None, ignore_functions=True):
    """
    Create a conditional block or a Category that assigns labels based on value thresholds.

    Args:
        variable (str): Variable to classify, with or without brackets.
        thresholds (list of float): Threshold values in ascending order. These define the boundaries between categories.
        categories (list of str): Category labels. Must have exactly one more element than thresholds.
        name (str, optional): Name for the output category. If provided, returns a Category; if None, returns the If block (conditional logic) for further encapsulation.
        comment (str, optional): Optional comment for the calculation. Used only if name is provided.
        ignore_functions (bool): If True, strings that appear to be function
            calls (e.g., "max([Au], [Ag])") are not wrapped in brackets.
            Defaults to True.

    Returns:
        Category or If: If name is provided, returns a pollywog Category with conditional logic for threshold-based classification. If name is None, returns the If block (conditional logic) for further use.

    Raises:
        ValueError: If len(categories) != len(thresholds) + 1.

    Example:
        >>> from pollywog.helpers import CategoryFromThresholds
        >>> CategoryFromThresholds("Au", [0.5, 1.0, 2.0], ["Waste", "Low Grade", "Medium Grade", "High Grade"], name="ore_class")
        >>> CategoryFromThresholds("Au", [0.5, 1.0, 2.0], ["Waste", "Low Grade", "Medium Grade", "High Grade"])
    """
    if len(categories) != len(thresholds) + 1:
        raise ValueError("categories must have one more element than thresholds")
    base_variable = variable
    variable = ensure_brackets(variable, ignore_functions=ignore_functions)
    rows = []
    prev = None
    for i, threshold in enumerate(thresholds):
        if prev is None:
            cond = f"{variable} <= {threshold}"
        else:
            cond = f"({variable} > {prev}) and ({variable} <= {threshold})"
        rows.append(([cond], [categories[i]]))
        prev = threshold
    otherwise = [categories[-1]]
    if_block = If([IfRow(cond, val) for cond, val in rows], otherwise=otherwise)
    if name is None:
        return if_block
    return Category(
        name,
        [if_block],
        comment_equation=comment or f"Classify {base_variable} by thresholds {thresholds}",
    )
