import copy
from pollywog.core import CalcSet, If, IfRow
import re


from pollywog.leapfrog_env import LEAPFROG_ENV


def run_calcset(
    calcset, inputs=None, dataframe=None, assign_results=True, output_variables=False
):
    """
    Evaluate a CalcSet with external inputs or a pandas DataFrame.

    This function executes a calculation set using either a dictionary of input values
    or a pandas DataFrame. When using a DataFrame, calculations are applied row-by-row.

    Args:
        calcset (CalcSet): The calculation set to evaluate.
        inputs (dict, optional): Dictionary of input variable values for single evaluation.
        dataframe (pd.DataFrame, optional): DataFrame for row-by-row evaluation.
        assign_results (bool): Whether to assign results to output. Defaults to True.
        output_variables (bool): Whether to include variables in output.
            Defaults to False (Leapfrog-like behavior: only calculations, categories, and filters).

    Returns:
        dict or pd.DataFrame:
            - If inputs provided: Dictionary of calculation results.
            - If dataframe provided: DataFrame with calculated columns added.

    Note:
        pandas is only required when using DataFrame input/output.

    Example:
        >>> from pollywog.core import CalcSet, Number
        >>> cs = CalcSet([Number("doubled", "[x] * 2")])
        >>> run_calcset(cs, inputs={"x": 5})
        {'doubled': 10}
    """

    # Helper to evaluate an expression or If object
    def eval_expr(expr, context):
        if isinstance(expr, str):
            if not expr.strip():
                return None

            # Replace [var] with context["var"] using regex
            def repl(m):
                var = m.group(1)
                return f"context[{repr(var)}]"

            expr_eval = re.sub(r"\[([^\]]+)\]", repl, expr)
            try:
                # Provide Leapfrog-like environment for eval
                return eval(expr_eval, {"context": context, **LEAPFROG_ENV}, context)
            except Exception:
                return None
        elif isinstance(expr, If):
            for row in expr.rows:
                cond = eval_expr(row.condition[0], context) if row.condition else True
                if cond:
                    return eval_expr(row.value[0], context)
            if expr.otherwise:
                return eval_expr(expr.otherwise[0], context)
            return None
        elif isinstance(expr, IfRow):
            # Should not be evaluated directly, only as part of If
            return None
        else:
            return expr

    # Dependency resolution
    sorted_items = calcset.topological_sort().items

    def run_single(context):
        results = {}
        for item in sorted_items:
            # If item is a Variable, assign its value from context or inputs directly
            if getattr(item, "item_type", None) == "variable":
                results[item.name] = context.get(item.name, None)
                continue
            child_results = []
            for child in item.expression:
                child_results.append(eval_expr(child, {**context, **results}))
            results[item.name] = child_results[0] if child_results else None
        # Filter output according to output_variables flag
        item_type_map = {
            item.name: getattr(item, "item_type", None) for item in sorted_items
        }
        if not output_variables:
            return {
                k: v for k, v in results.items() if item_type_map.get(k) != "variable"
            }
        return results

    if dataframe is not None:
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for DataFrame input/output. Please install pandas or use dict inputs."
            )
        df = dataframe.copy()
        for idx, row in df.iterrows():
            context = dict(row)
            results = run_single(context)
            for k, v in results.items():
                df.at[idx, k] = v
        # Remove variable columns if output_variables is False
        if not output_variables:
            variable_names = [
                item.name
                for item in sorted_items
                if getattr(item, "item_type", None) == "variable"
            ]
            df = df.drop(columns=variable_names, errors="ignore")
        return df
    else:
        context = inputs if inputs is not None else {}
        return run_single(context)


# Pandas DataFrame extension accessor
try:
    import pandas as pd

    @pd.api.extensions.register_dataframe_accessor("pw")
    class PollywogAccessor:
        """
        Pandas DataFrame accessor for running pollywog calculations.

        This accessor provides a convenient way to run CalcSets on DataFrames
        using the .pw namespace.

        Example:
            >>> import pandas as pd
            >>> from pollywog.core import CalcSet, Number
            >>> df = pd.DataFrame({'x': [1, 2, 3]})
            >>> cs = CalcSet([Number("doubled", "[x] * 2")])
            >>> result = df.pw.run(cs)
        """

        def __init__(self, pandas_obj):
            """
            Initialize the accessor with a DataFrame.

            Args:
                pandas_obj (pd.DataFrame): The DataFrame to operate on.
            """
            self._obj = pandas_obj

        def run(self, calcset, assign_results=True):
            """
            Run a CalcSet on this DataFrame, returning a copy with results assigned.

            Args:
                calcset (CalcSet): The calculation set to run.
                assign_results (bool): Whether to assign results to output. Defaults to True.

            Returns:
                pd.DataFrame: A copy of the DataFrame with calculated columns added.
            """
            return run_calcset(
                calcset, dataframe=self._obj, assign_results=assign_results
            )

except ImportError:
    pass
