import json
import re
import zlib
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
    Sequence,
    overload,
)

from .utils import ensure_list, ensure_str_list, to_dict

HEADER = b"\x25\x6c\x66\x63\x61\x6c\x63\x2d\x31\x2e\x30\x0a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

ITEM_ORDER = {
    "variable": 0,
    "calculation": 1,
    "filter": 2,
}


# TODO: check if items need to be sorted into variables then calculations then filters and do so if needed
# TODO: actually just sorted preemptively when writing to file, will check later if this is an issue
class CalcSet:
    """
    Represents a Leapfrog-style calculation set, containing variables, calculations, categories, filters, and conditional logic.

    CalcSet is the main container for building, manipulating, and exporting calculation workflows. It is designed to help automate large, complex, or repetitive calculation sets, and supports querying, dependency analysis, and rich display in Jupyter notebooks.

    Args:
        items (list of Item): List of calculation items (Number, Category, Filter, If, etc.)

    Example:
        >>> from pollywog.core import CalcSet, Number
        >>> calcset = CalcSet([
        ...     Number("Au_est", "block[Au] * 0.95"),
        ...     Number("Ag_est", "block[Ag] * 0.85")
        ... ])
    """

    def __init__(self, items: list["Item"]):
        """
        Initialize a CalcSet with a list of items.

        Args:
            items (list): List of calculation items (Number, Category, Variable, Filter, If, etc.).
        """
        self.items = ensure_list(items)

    def copy(self) -> "CalcSet":
        """
        Return a deep copy of the CalcSet and its items.

        Returns:
            CalcSet: A new CalcSet instance with all items copied.
        """
        return CalcSet([item.copy() for item in self.items])

    def query(self, expr: str, **external_vars) -> "CalcSet":
        """
        Filter items in the CalcSet using a query expression.

        The expression can use attributes of Item (e.g., 'item_type == "variable" and name.startswith("Au")'),
        and external variables using @var syntax (like pandas).

        Args:
            expr (str): Query expression to filter items.
            **external_vars: External variables to use in the query (referenced as @var).

        Returns:
            CalcSet: New CalcSet with filtered items.

        Example:
            >>> calcset.query('name.startswith("Au")')
        """
        import inspect
        import re

        filtered = []
        # Get caller's frame to access local and global variables
        frame = inspect.currentframe()
        try:
            caller_frame = frame.f_back if frame is not None else None
            caller_locals = caller_frame.f_locals if caller_frame else {}
            caller_globals = caller_frame.f_globals if caller_frame else {}
        finally:
            del frame

        # Merge external_vars with caller's scope, external_vars takes precedence
        merged_vars = dict(caller_globals)
        merged_vars.update(caller_locals)
        merged_vars.update(external_vars)

        # Safe helpers for query expressions
        SAFE_EVAL_HELPERS = {
            "len": len,
            "any": any,
            "all": all,
            "min": min,
            "max": max,
            "sorted": sorted,
            "re": re,
            "str": str,
        }

        def replace_at_var(match):
            var_name = match.group(1)
            if var_name in merged_vars:
                return f'merged_vars["{var_name}"]'
            else:
                raise NameError(f"External variable '@{var_name}' not provided.")

        expr_eval = re.sub(r"@([A-Za-z_][A-Za-z0-9_]*)", replace_at_var, expr)
        for item in self.items:
            ns = {k: getattr(item, k, None) for k in dir(item) if not k.startswith("_")}
            try:
                if eval(
                    expr_eval, {"merged_vars": merged_vars, **SAFE_EVAL_HELPERS}, ns
                ):
                    filtered.append(item)
            except Exception:
                pass
        return CalcSet(filtered)

    def topological_sort(self) -> "CalcSet":
        """
        Return a new CalcSet with items sorted topologically by dependencies.

        This method analyzes variable dependencies and reorders items so that each
        calculation appears after all the calculations it depends on. This ensures
        calculations can be evaluated in the correct order.

        Returns:
            CalcSet: New CalcSet with topologically sorted items.

        Raises:
            ValueError: If cyclic dependencies are detected (e.g., A depends on B and B depends on A).

        Example:
            >>> cs = CalcSet([
            ...     Number("result", "[intermediate] * 2"),
            ...     Number("intermediate", "[input] + 1")
            ... ])
            >>> sorted_cs = cs.topological_sort()
            # Now 'intermediate' will come before 'result'
        """
        items_by_name = {
            item.name: item for item in self.items if hasattr(item, "name")
        }
        sorted_items = []
        visited = set()
        temp_mark = set()

        def visit(item):
            if item.name in visited:
                return
            if item.name in temp_mark:
                raise ValueError(f"Cyclic dependency detected involving '{item.name}'")
            temp_mark.add(item.name)
            for dep in getattr(item, "dependencies", set()):
                if dep in items_by_name:
                    visit(items_by_name[dep])
            temp_mark.remove(item.name)
            visited.add(item.name)
            sorted_items.append(item)

        for item in self.items:
            visit(item)

        # Add items without a name (should be rare)
        unnamed = [item for item in self.items if not hasattr(item, "name")]
        sorted_items.extend(unnamed)

        return CalcSet(sorted_items)

    def to_dict(self, sort_items: bool = True) -> Dict[str, Any]:
        """
        Convert the CalcSet to a dictionary representation.

        Args:
            sort_items (bool): Whether to sort items by type.

        Returns:
            dict: Dictionary representation of the calculation set.
        """
        items = to_dict(self.items)
        if sort_items:
            items.sort(key=lambda x: ITEM_ORDER.get(x.get("type"), 99))
        return {"type": "calculation-set", "items": items}

    @classmethod
    def from_dict(cls: Type["CalcSet"], data: Dict[str, Any]) -> "CalcSet":
        """
        Create a CalcSet from a dictionary.

        Args:
            data (dict): Dictionary containing calculation set data.

        Returns:
            CalcSet: Instance of CalcSet.
        """
        if data["type"] != "calculation-set":
            raise ValueError(f"Expected type 'calculation-set', got {data['type']}")
        items = []
        for item in data["items"]:
            item_type = item["type"]
            if item_type in classes:
                items.append(classes[item_type].from_dict(item))
            elif item_type == "calculation":
                if item.get("calculation_type") == "number":
                    items.append(Number.from_dict(item))
                elif item.get("calculation_type") == "string":
                    items.append(Category.from_dict(item))
                else:
                    raise ValueError(
                        f"Unknown calculation type: {item.get('calculation_type')}"
                    )
            else:
                raise ValueError(f"Unknown item type: {item_type}")
        return cls(items=items)

    def to_json(self, sort_items: bool = True, indent: int = 0) -> str:
        """
        Convert the CalcSet to a JSON string.

        Args:
            sort_items (bool): Whether to sort items by type.
            indent (int): Indentation level for JSON output.

        Returns:
            str: JSON string representation.
        """
        return json.dumps(self.to_dict(sort_items=sort_items), indent=indent)

    def to_lfcalc(
        self, filepath_or_buffer: Union[str, Path, Any], sort_items: bool = True
    ) -> None:
        """
        Write the CalcSet to a Leapfrog .lfcalc file.

        Args:
            filepath_or_buffer (str, Path, or file-like): Output file path or buffer.
            sort_items (bool): Whether to sort items by type.
        """
        if isinstance(filepath_or_buffer, (str, Path)):
            with open(filepath_or_buffer, "wb") as f:
                self._write_to_file(f, sort_items=sort_items)
        else:
            self._write_to_file(filepath_or_buffer, sort_items=sort_items)

    def _write_to_file(self, file: Any, sort_items: bool) -> None:
        """
        Write the CalcSet to a file in Leapfrog binary format.

        This internal method writes the CalcSet as compressed JSON data with
        a Leapfrog-specific header for .lfcalc files.

        Args:
            file (file-like): File object to write to.
            sort_items (bool): Whether to sort items by type (variable, calculation, filter).
        """
        compressed_data = zlib.compress(
            self.to_json(sort_items=sort_items).encode("utf-8")
        )
        file.write(HEADER)
        file.write(compressed_data)

    @staticmethod
    def read_lfcalc(filepath_or_buffer: Union[str, Path, Any]) -> "CalcSet":
        """
        Read a Leapfrog .lfcalc file and return a CalcSet.

        Args:
            filepath_or_buffer (str, Path, or file-like): Input file path or buffer.

        Returns:
            CalcSet: Instance of CalcSet.
        """
        if isinstance(filepath_or_buffer, (str, Path)):
            with open(filepath_or_buffer, "rb") as f:
                return CalcSet._read_from_file(f)
        else:
            return CalcSet._read_from_file(filepath_or_buffer)

    @staticmethod
    def _read_from_file(file: Any) -> "CalcSet":
        """
        Read a CalcSet from a Leapfrog binary file object.

        This internal method reads compressed JSON data from a .lfcalc file,
        decompresses it, and reconstructs the CalcSet.

        Args:
            file (file-like): File object to read from.

        Returns:
            CalcSet: Reconstructed CalcSet instance.
        """
        file.seek(len(HEADER))
        compressed_data = file.read()
        json_data = zlib.decompress(compressed_data).decode("utf-8")
        data = json.loads(json_data)
        return CalcSet.from_dict(data)

    def __repr__(self) -> str:
        """
        Return a pretty-printed JSON string representation of the CalcSet.
        """
        return self.to_json(indent=2)

    def _repr_html_(self) -> str:
        """
        Return HTML representation for Jupyter notebook rich display.

        Returns:
            str: HTML string for displaying the CalcSet.
        """
        try:
            from pollywog.display import display_calcset
            return display_calcset(self, display_output=False)
        except ImportError:
            # If display module isn't available, fall back to text representation
            return f"<pre>{repr(self)}</pre>"

    def __add__(self, other: "CalcSet") -> "CalcSet":
        """
        Add two CalcSet objects together, combining their items.
        Args:
            other (CalcSet): Another CalcSet instance.
        Returns:
            CalcSet: New CalcSet with combined items.
        """
        if not isinstance(other, CalcSet):
            return NotImplemented
        items1 = list(self.items) if self.items else []
        items2 = list(other.items) if other.items else []
        return CalcSet(items1 + items2)

    def __getitem__(self, name: str) -> "Item":
        """
        Get an item by name.

        Args:
            name (str): Name of the item to retrieve.

        Returns:
            Item: The item with the specified name.

        Raises:
            KeyError: If no item with the specified name exists.
        """
        for item in self.items:
            if hasattr(item, "name") and item.name == name:
                return item
        raise KeyError(f"Item with name '{name}' not found.")

    def __setitem__(self, name: str, value: "Item") -> None:
        """
        Set or replace an item by name.

        Args:
            name (str): Name of the item to set.
            value (Item): The new item to set.
        """
        named_item = value.replace(name=name)
        for i, item in enumerate(self.items):
            if hasattr(item, "name") and item.name == name:
                self.items[i] = named_item
                return
        else:
            self.items.append(named_item)

    def rename(
        self,
        items: Optional[Union[Dict[str, str], Callable[[str], Optional[str]]]] = None,
        variables: Optional[
            Union[Dict[str, str], Callable[[str], Optional[str]]]
        ] = None,
        regex: bool = False,
    ) -> "CalcSet":
        """
        Return a copy of the CalcSet with specified items renamed and/or variables in expression renamed.

        Args:
            items (dict-like or function): Mapping of old item names to new names.
            variables (dict-like or function): Mapping of old variable names to new names.
            regex (bool): Whether to treat keys in `items` and `variables` as regex patterns.

        Returns:
            CalcSet: New instance with updated item names and/or expression.
        """
        new_items = []
        for item in self.items:
            name = item.name
            # Rename item names
            if items is not None:
                if callable(items):
                    new_name = items(name)
                    if new_name is not None:
                        name = new_name
                elif regex:
                    for pattern, replacement in items.items():
                        new_name = re.sub(pattern, replacement, name)
                        if new_name != name:
                            name = new_name
                else:
                    if name in items:
                        name = items[name]
            # Rename item name using variables mapping for any Item subclass
            var_name = name
            if variables is not None and isinstance(item, Item):
                if callable(variables):
                    new_var_name = variables(var_name)
                    if new_var_name is not None:
                        var_name = new_var_name
                elif regex:
                    for pattern, replacement in variables.items():
                        new_var_name = re.sub(pattern, replacement, var_name)
                        if new_var_name != var_name:
                            var_name = new_var_name
                else:
                    if var_name in variables:
                        var_name = variables[var_name]
            # Use var_name for all Item subclasses
            final_name = var_name if isinstance(item, Item) else name
            new_items.append(
                item.rename(name=final_name, variables=variables, regex=regex)  # type: ignore
            )
        return CalcSet(new_items)


class Item:
    """
    Base class for all items in a CalcSet.

    Subclasses represent specific calculation types (Number, Category, Variable, Filter, If, etc.).
    Each item has a name, expressions, and optional comments.

    The `expression` parameter can be either a string or a list:
    - Use a string for simple expressions: ``Number("result", "[x] * 2")``
    - Use a list when including If objects for conditional logic: ``Number("result", [If(...)])``

    Strings are automatically converted to single-element lists internally, but If objects
    are separate structures that cannot be embedded in expression strings, which is why
    the parameter accepts lists.

    Attributes:
        name (str): Name of the item.
        expression (list): List of expressions/statements (internally stored as a list).
        comment_item (str): Comment for the item.
        comment_equation (str): Comment for the equation.
    """

    item_type = None
    calculation_type = None

    def __init__(
        self,
        name: str = "",
        expression: Optional[List[Any]] = None,
        comment_item: str = "",
        comment_equation: str = "",
    ):
        """
        Initialize an Item.

        Args:
            name (str): Name of the item (e.g., variable name or calculation name).
            expression (str or list, optional): Expression(s) to evaluate. Can be:
                - A string containing a Leapfrog expression (e.g., "[Au] * 2")
                - A list of strings for multiple expressions
                - A list containing If objects for conditional logic
                The parameter accepts both strings and lists because If statements are
                separate objects that cannot be embedded in expression strings.
                Single strings are automatically wrapped in a list internally.
            comment_item (str): Comment describing the item itself. Defaults to empty string.
            comment_equation (str): Comment describing the equation/logic. Defaults to empty string.
        """
        self.name = name
        if expression is None:
            expression = []
        self.expression = ensure_list(expression)
        self.comment_item = comment_item
        self.comment_equation = comment_equation

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Item to a dictionary representation.

        Returns:
            dict: Dictionary representation of the item.
        """
        if self.item_type is None:
            raise NotImplementedError("item_type must be defined in subclass")
        children = to_dict(self.expression, guard_strings=True)
        item = {
            "type": self.item_type,
            "name": self.name,
            "equation": {
                "type": "equation",
                "comment": self.comment_equation,
                "statement": {
                    "type": "list",
                    "children": children,
                },
            },
            "comment": self.comment_item,
        }
        if self.calculation_type:
            item["calculation_type"] = self.calculation_type
        return item

    @classmethod
    def from_dict(cls: Type["Item"], data: Dict[str, Any]) -> "Item":
        """
        Create an Item from a dictionary.

        Args:
            data (dict): Dictionary containing item data.

        Returns:
            Item: Instance of Item or subclass.
        """
        if cls.item_type is None:
            raise NotImplementedError("item_type must be defined in subclass")
        if data["type"] != cls.item_type:
            raise ValueError(f"Expected item type {cls.item_type}, got {data['type']}")
        expression = []
        for child in ensure_list(data["equation"]["statement"]["children"]):
            expression.append(dispatch_expression(child))
        return cls(
            name=data["name"],
            expression=expression,
            comment_item=data.get("comment", ""),
            comment_equation=data["equation"].get("comment", ""),
        )

    @property
    def dependencies(self) -> Set[str]:
        """
        Get the set of variable dependencies for this item.

        Returns:
            set: Set of variable names that are dependencies.
        """
        return get_dependencies(self)

    def copy(self) -> "Item":
        """
        Return a deep copy of the Item.

        Returns:
            Item: A new Item instance with all attributes copied.
        """
        return type(self)(
            name=self.name,
            expression=[c.copy() if hasattr(c, "copy") else c for c in self.expression],
            comment_item=self.comment_item,
            comment_equation=self.comment_equation,
        )

    def replace(self, **changes: Any) -> "Item":
        """
        Return a copy of the Item with specified attributes replaced.

        Args:
            **changes: Attributes to replace.

        Returns:
            Item: New instance with updated attributes.
        """
        params = {
            "name": self.name,
            "expression": self.expression,
            "comment_item": self.comment_item,
            "comment_equation": self.comment_equation,
        }
        params.update(changes)
        return type(self)(**params)

    def rename(
        self,
        name: Optional[str] = None,
        variables: Optional[
            Union[Dict[str, str], Callable[[str], Optional[str]]]
        ] = None,
        regex: bool = False,
    ) -> "Item":
        """
        Return a copy of the Item with a new name and/or renamed variables in expression.

        Args:
            name (str): New name for the item.
            variables (dict-like or function): Mapping of old variable names to new names.
            regex (bool): Whether to treat keys in `variables` as regex patterns.

        Returns:
            Item: New instance with updated name and/or expression.
        """
        new = self.copy()
        # For any Item subclass, allow variable renaming to affect the name
        if name is not None:
            new.name = name
        elif variables is not None and isinstance(self, Item):
            var_name = new.name
            if callable(variables):
                new_var_name = variables(var_name)
                if new_var_name is not None:
                    new.name = new_var_name
            elif regex:
                for pattern, replacement in variables.items():
                    new_var_name = re.sub(pattern, replacement, var_name)
                    if new_var_name != var_name:
                        var_name = new_var_name
                new.name = var_name
            else:
                if var_name in variables:
                    new.name = variables[var_name]
        if variables is not None:
            return rename(new, variables, regex=regex)  # type: ignore
        return new

    def _repr_html_(self) -> str:
        """
        Return HTML representation for Jupyter notebook rich display.

        Returns:
            str: HTML string for displaying the item.
        """
        try:
            from pollywog.display import display_item
            return display_item(self, display_output=False)
        except ImportError:
            # If display module isn't available, fall back to text representation
            return f"<pre>{repr(self)}</pre>"


class IfRow:
    """
    Represents a single row in an If block, containing a condition and corresponding value(s).

    Args:
        condition (list): Condition expressions.
        value (list): Value expressions if condition is met.
    """

    def __init__(self, condition: List[Any], value: List[Any]):
        """
        Initialize an IfRow (a single row in an If block).

        Args:
            condition (list): Condition expressions that must evaluate to True for this row to execute.
            value (list): Value expressions to return if the condition is met.
        """
        self.condition = condition
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the IfRow to a dictionary representation.

        Returns:
            dict: Dictionary representation of the IfRow.
        """
        return {
            "type": "if_row",
            "test": {"type": "list", "children": to_dict(self.condition)},
            "result": {
                "type": "list",
                "children": to_dict(self.value, guard_strings=True),
            },
        }

    @classmethod
    def from_dict(cls: Type["IfRow"], data: Dict[str, Any]) -> "IfRow":
        """
        Create an IfRow from a dictionary.

        Args:
            data (dict): Dictionary containing IfRow data.

        Returns:
            IfRow: Instance of IfRow.
        """
        if data["type"] != "if_row":
            raise ValueError(f"Expected type 'if_row', got {data['type']}")
        # return cls(
        #     condition=data["test"]["children"],
        #     value=data["result"]["children"],
        # )
        condition = []
        for cond in ensure_list(data["test"]["children"]):
            condition.append(dispatch_expression(cond))
        value = []
        for val in ensure_str_list(data["result"]["children"]):
            value.append(dispatch_expression(val))
        return cls(condition=condition, value=value)

    def copy(self) -> "IfRow":
        """
        Return a deep copy of the IfRow.

        Returns:
            IfRow: A new IfRow instance with copied condition and value expressions.
        """
        return IfRow(
            condition=[c.copy() if hasattr(c, "copy") else c for c in self.condition],
            value=[v.copy() if hasattr(v, "copy") else v for v in self.value],
        )


class If:
    """
    Represents a conditional logic block (if/else) in a calculation set.

    Args:
        rows (list): List of IfRow objects, dicts, or (condition, value) tuples.
        otherwise (list): Expressions for the 'otherwise' case.

    Alternatively, in case of a single condition and value, these may be provided directly as three parameters:

    Args:
        condition: condition expression.
        then: value expression if condition is met.
        otherwise: value expression if no conditions are met.

    Example:
        >>> from pollywog.core import If, Number
        >>> if_block = If([
        ...     ("[Au] > 1", "[Au] * 1.1"),
        ...     ("[Au] <= 1", "[Au] * 0.9")
        ... ], otherwise=["[Au]"])

    Example of the second case:
        >>> from pollywog.core import If, Number
        >>> if_block = If("[Au] > 1", "[Au] * 1.1", "[Au]")
    """

    @overload
    def __init__(self, rows: List[Any], otherwise: List[Any]): ...
    @overload
    def __init__(self, condition: str, then: str, otherwise: str): ...
    def __init__(self, *args: Any, **kwargs: Any):
        """
        Initialize an If expression.
        Args:
            rows (list): List of either IfRow objects, dicts, or (condition, value) tuples.
            otherwise (list): Expressions for the 'otherwise' case.

        Alternatively, in case of a single condition and value, these may be provided directly as three parameters:

        Args:
            condition: condition expression.
            then: value expression if condition is met.
            otherwise: value expression if no conditions are met.
        """

        args_list = list(args)
        if len(args) + len(kwargs) == 2:
            rows = kwargs["rows"] if "rows" in kwargs else args_list.pop(0)
            otherwise = (
                kwargs["otherwise"] if "otherwise" in kwargs else args_list.pop(0)
            )
        elif len(args) + len(kwargs) == 3:
            condition = (
                kwargs["condition"] if "condition" in kwargs else args_list.pop(0)
            )
            then = kwargs["then"] if "then" in kwargs else args_list.pop(0)
            otherwise = (
                kwargs["otherwise"] if "otherwise" in kwargs else args_list.pop(0)
            )
            rows = [(condition, then)]
        else:
            raise ValueError(
                "If must be initialized with either (rows, otherwise) or (condition, then, otherwise)"
            )
        ifrows = []
        for row in ensure_list(rows):
            if isinstance(row, IfRow):
                ifrows.append(row)
            elif isinstance(row, dict) and row.get("type") == "if_row":
                ifrows.append(IfRow.from_dict(row))
            elif isinstance(row, (tuple, list)) and len(row) == 2:
                condition, value = row
                ifrows.append(IfRow(condition, value))
            else:
                raise ValueError(f"Invalid row format: {row}")
        self.rows = ifrows
        self.otherwise = otherwise

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the If expression to a dictionary representation.

        Returns:
            dict: Dictionary representation of the If expression.
        """
        rows = [row.to_dict() for row in self.rows]
        return {
            "type": "if",
            "rows": rows,
            "otherwise": {
                "type": "list",
                "children": to_dict(self.otherwise, guard_strings=True),
            },
        }

    @classmethod
    def from_dict(cls: Type["If"], data: Dict[str, Any]) -> "If":
        """
        Create an If expression from a dictionary.

        Args:
            data (dict): Dictionary containing If expression data.

        Returns:
            If: Instance of If.
        """
        if data["type"] != "if":
            raise ValueError(f"Expected type 'if', got {data['type']}")
        rows = [
            IfRow.from_dict(row) if isinstance(row, dict) else row
            for row in ensure_list(data["rows"])
        ]
        otherwise = []
        for val in ensure_str_list(data["otherwise"]["children"]):
            otherwise.append(dispatch_expression(val))
        return cls(rows=rows, otherwise=otherwise)

    def copy(self) -> "If":
        """
        Return a deep copy of the If expression.

        Returns:
            If: A new If instance with copied rows and otherwise expressions.
        """
        return If(
            rows=[r.copy() if hasattr(r, "copy") else r for r in self.rows],
            otherwise=[o.copy() if hasattr(o, "copy") else o for o in self.otherwise],
        )


class Number(Item):
    """
    Represents a numeric calculation item in a CalcSet.

    Used for calculations whose values are numbers, either integers or floats.
    This is the most common type of calculation in Leapfrog calculation sets.

    Example:
        >>> from pollywog.core import Number
        >>> # Simple expression using positional arguments
        >>> au_calc = Number("Au_adjusted", "[Au] * 0.95")
        >>> # With comment
        >>> au_calc = Number("Au_adjusted", "[Au] * 0.95", comment_equation="Apply dilution")
    """

    item_type = "calculation"
    calculation_type = "number"


class Category(Item):
    """
    Represents a categorical (string) calculation item in a CalcSet.

    Used for calculations whose values are categories or text labels.
    Commonly used for classification, domain assignment, or text manipulation.

    Example:
        >>> from pollywog.core import Category, If
        >>> # Simple string category
        >>> domain = Category("rock_type", "'granite'")
        >>> # Conditional category using If (requires list)
        >>> grade_class = Category("grade_class", [If("[Au] > 1", "High", "Low")])
    """

    item_type = "calculation"
    calculation_type = "string"


class Variable(Item):
    """
    Represents a variable item in a calculation set.

    Variables can perform calculations but are not available outside the scope
    of the calculation set. They are typically used as parameters or intermediate
    values that are referenced by other calculations.

    Example:
        >>> from pollywog.core import Variable
        >>> au_var = Variable(name="Au", comment_item="Gold grade from drillhole database")
    """

    item_type = "variable"


class Filter(Item):
    """
    Represents a filter item in a calculation set.

    Filters define conditions that restrict or modify which data is included
    in calculations. They evaluate to boolean values.

    Example:
        >>> from pollywog.core import Filter
        >>> ore_filter = Filter("is_ore", "[Au] > 0.5")
    """

    item_type = "filter"


classes = {
    # "calculation": Item,
    "variable": Variable,
    "filter": Filter,
    "if": If,
    "if_row": IfRow,
}


expressions = {
    "if": If,
}


def dispatch_expression(data: Any) -> Any:
    """
    Dispatch an expression dictionary to the appropriate class constructor.

    Args:
        data (dict or any): Expression data.

    Returns:
        object: Instantiated expression object or the original data if not a dict.
    """
    if isinstance(data, dict) and "type" in data:
        expr_type = data["type"]
        if expr_type in expressions:
            return expressions[expr_type].from_dict(data)
        else:
            raise ValueError(f"Unknown expression type: {expr_type}")
    return data


def get_dependencies(item: Any) -> Set[str]:
    """
    Recursively extract variable dependencies from an Item or expression.

    Args:
        item (Item or expression): The item or expression to analyze.

    Returns:
        set: Set of variable names that are dependencies.
    """
    deps = set()

    if isinstance(item, Item):
        for child in item.expression:
            deps.update(get_dependencies(child))
    elif isinstance(item, If):
        for row in item.rows:
            deps.update(get_dependencies(row))
        deps.update(get_dependencies(item.otherwise))
    elif isinstance(item, IfRow):
        deps.update(get_dependencies(item.condition))
        deps.update(get_dependencies(item.value))
    elif isinstance(item, list):
        for elem in item:
            deps.update(get_dependencies(elem))
    elif isinstance(item, str):
        # Find all occurrences of [var_name] in the string
        found_vars = re.findall(r"\[([^\[\]]+)\]", item)
        deps.update(found_vars)

    return deps


def rename(
    item: Any, mapper: Union[Dict[str, str], Callable[[str], str]], regex: bool = False
) -> Any:
    """
    Recursively rename variables in an Item or expression based on a mapping dictionary.

    Args:
        item (Item or expression): The item or expression to rename.
        mapper (dict-like or function): Mapping of old variable names to new names.
        regex (bool): If True, treat keys and values of the mapper as regular expressions.

    Returns:
        Item or expression: The renamed item or expression.
    """
    if isinstance(item, Item):
        new_expression = [
            rename(child, mapper, regex=regex) for child in item.expression
        ]
        return item.replace(expression=new_expression)
    elif isinstance(item, If):
        new_rows = [rename(row, mapper, regex=regex) for row in item.rows]
        new_otherwise = rename(item.otherwise, mapper, regex=regex)
        return If(rows=new_rows, otherwise=new_otherwise)
    elif isinstance(item, IfRow):
        new_condition = rename(item.condition, mapper, regex=regex)
        new_value = rename(item.value, mapper, regex=regex)
        return IfRow(condition=new_condition, value=new_value)
    elif isinstance(item, list):
        return [rename(elem, mapper, regex=regex) for elem in item]
    elif isinstance(item, str):

        def replace_var(match):
            var_name = match.group(1)
            if callable(mapper):
                return f"[{mapper(var_name)}]"
            elif regex:
                for pattern, replacement in mapper.items():
                    var_name = re.sub(pattern, replacement, var_name)
                return f"[{var_name}]"
            else:
                return f"[{mapper.get(var_name, var_name)}]"

        return re.sub(r"\[([^\[\]]+)\]", replace_var, item)
    else:
        return item
