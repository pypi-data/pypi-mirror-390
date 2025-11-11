from ..core import If, IfRow, Variable, Number, Category

try:
    import sklearn
except ImportError:
    raise ImportError(
        "scikit-learn is required for conversion. Please install it via 'pip install scikit-learn'."
    )


# Classification and Regression Trees

from sklearn import tree, ensemble


def convert_tree(
    tree_model,
    feature_names,
    target_name,
    flat=False,
    comment_equation=None,
    output_type=None,
):
    """
    Convert a scikit-learn decision tree to a Pollywog Number or Category.

    This function converts DecisionTreeRegressor and DecisionTreeClassifier models
    into Pollywog calculation items that can be exported to Leapfrog.

    Args:
        tree_model: A fitted DecisionTreeRegressor or DecisionTreeClassifier from scikit-learn.
        feature_names (list of str): List of feature names used in the model.
        target_name (str): Name of the target variable to create.
        flat (bool): Whether to create flattened if expressions (one condition per path).
            If True, creates a flat list of conditions. If False (default), creates nested If structure.
        comment_equation (str, optional): Comment for the generated equation.
            Defaults to "Converted from <ModelClassName>".
        output_type (class, optional): Output class to use (Number, Category, Variable).
            If None, automatically selects based on model type.

    Returns:
        Number or Category: A Pollywog calculation item representing the decision tree.

    Raises:
        ValueError: If tree_model is not a supported tree model type.

    Example:
        >>> from sklearn.tree import DecisionTreeRegressor
        >>> from pollywog.conversion.sklearn import convert_tree
        >>> model = DecisionTreeRegressor()
        >>> model.fit(X, y)
        >>> calc = convert_tree(model, ["feature1", "feature2"], "prediction")
    """
    tree_ = tree_model.tree_
    feature_name = [
        feature_names[i] if i != tree._tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]

    is_classifier = hasattr(tree_model, "classes_")
    classes = None
    if is_classifier:
        classes = tree_model.classes_

    if flat:
        # Create a flat list of conditions and values
        conditions = []
        values = []

        def recurse_flat(node, current_conditions):
            if tree_.feature[node] != tree._tree.TREE_UNDEFINED:
                name = feature_name[node]
                threshold = tree_.threshold[node]
                left_conditions = current_conditions + [f"[{name}] <= {threshold}"]
                right_conditions = current_conditions + [f"[{name}] > {threshold}"]
                recurse_flat(tree_.children_left[node], left_conditions)
                recurse_flat(tree_.children_right[node], right_conditions)
            else:
                value = (
                    tree_.value[node][0][0]
                    if not is_classifier
                    else classes[tree_.value[node][0].argmax()]
                )
                value = f'"{value}"' if isinstance(value, str) else str(value)
                conditions.append(
                    " and ".join(current_conditions) if current_conditions else "True"
                )
                values.append(value)

        recurse_flat(0, [])
        if_rows = [IfRow([cond], [val]) for cond, val in zip(conditions, values)]
        if_rows = If(if_rows, otherwise=["blank"])
    else:
        # Create nested If structure
        def recurse(node):
            if tree_.feature[node] != tree._tree.TREE_UNDEFINED:
                name = feature_name[node]
                threshold = tree_.threshold[node]
                left = recurse(tree_.children_left[node])
                right = recurse(tree_.children_right[node])
                return If(IfRow(f"[{name}] <= {threshold}", left), right)
            else:
                value = (
                    tree_.value[node][0][0]
                    if not is_classifier
                    else classes[tree_.value[node][0].argmax()]
                )
                value = f'"{value}"' if isinstance(value, str) else str(value)
                return value

        if_rows = recurse(0)

    if comment_equation is None:
        comment_equation = f"Converted from {tree_model.__class__.__name__}"

    if output_type is not None:
        return output_type(target_name, if_rows, comment_equation=comment_equation)

    if isinstance(tree_model, tree.DecisionTreeRegressor):
        return Number(target_name, if_rows, comment_equation=comment_equation)
    elif isinstance(tree_model, tree.DecisionTreeClassifier):
        return Category(target_name, if_rows, comment_equation=comment_equation)
    else:
        raise ValueError("Unsupported tree model type")


def convert_forest(
    forest_model, feature_names, target_name, flat=False, comment_equation=None
):
    """
    Convert a scikit-learn random forest to Pollywog Variables and a final Number/Category.

    This function converts RandomForestRegressor and RandomForestClassifier models
    into a list of Pollywog items, with each tree converted to a Variable and a final
    aggregation step (averaging for regression, majority vote for classification).

    Args:
        forest_model: A fitted RandomForestRegressor or RandomForestClassifier from scikit-learn.
        feature_names (list of str): List of feature names used in the model.
        target_name (str): Name of the target variable to create.
        flat (bool): Whether to create flattened if expressions for each tree.
            Defaults to False.
        comment_equation (str, optional): Comment for the generated equation.
            Defaults to model-specific description.

    Returns:
        list: List of Pollywog items including Variables for each tree and a final
            Number (for regression) or Category (for classification) for the aggregated result.

    Raises:
        ValueError: If forest_model is not a RandomForestRegressor or RandomForestClassifier.

    Example:
        >>> from sklearn.ensemble import RandomForestRegressor
        >>> from pollywog.conversion.sklearn import convert_forest
        >>> model = RandomForestRegressor(n_estimators=10)
        >>> model.fit(X, y)
        >>> calcs = convert_forest(model, ["feat1", "feat2"], "prediction")
    """
    if not isinstance(
        forest_model, (ensemble.RandomForestRegressor, ensemble.RandomForestClassifier)
    ):
        raise ValueError(
            "forest_model must be a RandomForestRegressor or RandomForestClassifier"
        )

    # Convert each tree in the forest
    trees = [
        convert_tree(
            estimator,
            feature_names,
            f"{target_name}_tree_{i}",
            flat=flat,
            comment_equation=f"Tree {i} from {forest_model.__class__.__name__}",
            output_type=Variable,
        )
        for i, estimator in enumerate(forest_model.estimators_)
    ]

    # Average predictions for regression or majority vote for classification
    if isinstance(forest_model, ensemble.RandomForestRegressor):
        # For regression, create an equation that averages the tree outputs
        tree_outputs = " + ".join([f"[{t.name}]" for t in trees])
        equation = f"({tree_outputs}) / {len(trees)}"
        return trees + [
            Number(
                target_name,
                [equation],
                comment_equation=f"Averaged output from {len(trees)} trees in {forest_model.__class__.__name__}",
            )
        ]
    elif isinstance(forest_model, ensemble.RandomForestClassifier):
        # For classification, create an equation that does majority voting
        tree_outputs = " + ".join([f"[{t.name}]" for t in trees])
        equation = f"round(({tree_outputs}) / {len(trees)})"
        return trees + [
            Category(
                target_name,
                [equation],
                comment_equation=f"Majority vote from {len(trees)} trees in {forest_model.__class__.__name__}",
            )
        ]


# Linear Models
from sklearn import linear_model


def convert_linear_model(lm_model, feature_names, target_name):
    """
    Convert a scikit-learn linear model to a Pollywog Number.

    This function converts fitted linear models (LinearRegression, Ridge, Lasso, etc.)
    into a Pollywog Number calculation representing the linear equation.

    Args:
        lm_model: A fitted linear model from scikit-learn with coef_ and intercept_ attributes.
        feature_names (list of str): List of feature names corresponding to the coefficients.
        target_name (str): Name of the target variable to create.

    Returns:
        Number: A Pollywog Number representing the linear equation.

    Example:
        >>> from sklearn.linear_model import LinearRegression
        >>> from pollywog.conversion.sklearn import convert_linear_model
        >>> model = LinearRegression()
        >>> model.fit(X, y)
        >>> calc = convert_linear_model(model, ["feature1", "feature2"], "prediction")
    """
    coefs = lm_model.coef_
    intercept = lm_model.intercept_

    def format_float(val):
        return f"{float(val):.6f}"

    terms = [format_float(intercept)] if intercept != 0 else []
    for coef, feature in zip(coefs, feature_names):
        if coef != 0:
            terms.append(f"{format_float(coef)} * [{feature}]")

    equation = " + ".join(terms) if terms else "0"
    return Number(
        target_name,
        [equation],
        comment_equation=f"Converted from {lm_model.__class__.__name__}",
    )


# Pre Processing
