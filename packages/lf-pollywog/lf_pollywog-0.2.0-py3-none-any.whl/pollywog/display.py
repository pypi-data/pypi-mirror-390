_DISPLAY_THEME = "light"


def set_theme(theme):
    """
    Set the global theme for display_calcset.

    Args:
        theme (str): Theme name, either "light" or "dark".

    Raises:
        ValueError: If theme is not "light" or "dark".
    """
    global _DISPLAY_THEME
    if theme not in ("light", "dark"):
        raise ValueError("Theme must be 'light' or 'dark'.")
    _DISPLAY_THEME = theme


def get_color_palette(theme=None, colors=None):
    """
    Get the color palette for a given theme.

    Args:
        theme (str, optional): Visual theme, either "light" or "dark".
            If None, uses the global theme. Defaults to None.
        colors (dict, optional): Custom color palette to override theme defaults.
            Defaults to None.

    Returns:
        dict: Color palette with keys for 'background', 'text', 'variable', etc.
    """
    default_colors = {
        "light": {
            "background": "#eee",
            "text": "#222",
            "variable": "#0057b7",
            "label": "#222",
            "if": "#0057b7",
            "arrow": "#222",
            "comment": "#999",
            "var_ref": "#b77",
        },
        "dark": {
            "background": "#222",
            "text": "#eee",
            "variable": "#7abaff",
            "label": "#eee",
            "if": "#7abaff",
            "arrow": "#eee",
            "comment": "#bbb",
            "var_ref": "#ffb77a",
        },
    }
    use_theme = theme if theme is not None else _DISPLAY_THEME
    palette = default_colors.get(use_theme, default_colors["light"]).copy()
    if colors:
        palette.update(colors)
    return palette


def render_expression(expr, palette, indent=0):
    """
    Render an expression as HTML with syntax highlighting.

    Args:
        expr: Expression to render (string, list, dict, or other).
        palette (dict): Color palette for styling.
        indent (int): Indentation level. Defaults to 0.

    Returns:
        str: HTML representation of the expression.
    """
    import html

    pad = "&nbsp;" * (indent * 4)
    if isinstance(expr, str):
        expr = html.escape(expr)
        expr = expr.replace(
            "[", f'<span style="color:{palette["var_ref"]};">['
        ).replace("]", "]</span>")
        return pad + f'<span style="color:{palette["text"]};">{expr}</span>'
    elif isinstance(expr, list):
        return "<br>".join(render_expression(e, palette, indent) for e in expr)
    if isinstance(expr, dict):
        typ = expr.get("type")
        if typ == "if":
            rows = expr.get("rows", [])
            otherwise = expr.get("otherwise", {}).get("children", [])
            html_rows = []
            for row in rows:
                cond = row.get("test", {}).get("children", [])
                res = row.get("result", {}).get("children", [])
                html_rows.append(
                    f'<div style="margin-left:{indent*24}px;border-left:2px solid {palette["if"]};padding-left:8px;">'
                    f'<span style="color:{palette["if"]};">if</span> '
                    f"{render_expression(cond, palette, 0)} "
                    f'<span style="color:{palette["arrow"]};">&rarr;</span> '
                    f"{render_expression(res, palette, indent+1)}"
                    f"</div>"
                )
            if otherwise:
                html_rows.append(
                    f'<div style="margin-left:{indent*24}px;border-left:2px solid {palette["if"]};padding-left:8px;">'
                    f'<span style="color:{palette["if"]};">otherwise</span> '
                    f'<span style="color:{palette["arrow"]};">&rarr;</span> '
                    f"{render_expression(otherwise, palette, indent+1)}"
                    f"</div>"
                )
            return "".join(html_rows)
        elif typ == "if_row":
            cond = expr.get("test", {}).get("children", [])
            res = expr.get("result", {}).get("children", [])
            return (
                f'<div style="margin-left:{indent*24}px;border-left:2px solid {palette["if"]};padding-left:8px;">'
                f'<span style="color:{palette["if"]};">if</span> '
                f"{render_expression(cond, palette, 0)} "
                f'<span style="color:{palette["arrow"]};">&rarr;</span> '
                f"{render_expression(res, palette, indent+1)}"
                f"</div>"
            )
        elif typ == "list":
            children = expr.get("children", [])
            return render_expression(children, palette, indent)
        else:
            return (
                pad
                + f'<span style="color:{palette["text"]};">{html.escape(str(expr))}</span>'
            )
    else:
        return (
            pad
            + f'<span style="color:{palette["text"]};">{html.escape(str(expr))}</span>'
        )


def render_equation(eq, palette):
    """
    Render an equation as HTML.

    Args:
        eq: Equation to render (dict or other).
        palette (dict): Color palette for styling.

    Returns:
        str: HTML representation of the equation.
    """
    import html

    if isinstance(eq, dict) and eq.get("type") == "equation":
        statement = eq["statement"]
        comment = eq.get("comment", "")
        expr_html = render_expression(statement, palette)
        comment_html = (
            f'<span style="color:{palette["comment"]};">{html.escape(comment)}</span>'
            if comment
            else ""
        )
        return f'<div style="margin-left:1em;color:{palette["text"]};">{expr_html} {comment_html}</div>'
    return html.escape(str(eq))


def render_item(item, palette):
    """
    Render a single Item (Number, Category, Variable, Filter, etc.) as HTML.

    Args:
        item: The item to render (must have to_dict() method).
        palette (dict): Color palette for styling.

    Returns:
        str: HTML representation of the item.
    """
    import html

    d = item.to_dict() if hasattr(item, "to_dict") else item
    name = d.get("name", "")
    typ = d.get("type", "")
    eq = d.get("equation", None)
    comment = d.get("comment", "")
    
    html_block = f'<div style="margin-bottom:0.5em;">'
    html_block += f'<b style="color:{palette["variable"]};">{html.escape(name)}</b> '
    
    # Show calculation_type for calculation items
    calc_type = d.get("calculation_type")
    label = typ
    if typ == "calculation" and calc_type:
        label = calc_type
    html_block += f'<span style="background:{palette["background"]};border-radius:4px;padding:2px 6px;color:{palette["label"]};">{html.escape(label)}</span>'
    
    if eq:
        html_block += render_equation(eq, palette)
    if comment:
        html_block += (
            f'<div style="color:{palette["comment"]};margin-left:1em;">{html.escape(comment)}</div>'
        )
    html_block += "</div>"
    return html_block


def display_item(item, theme=None, colors=None, display_output=True):
    """
    Display a single Item (Number, Category, Variable, Filter, etc.) in a Jupyter notebook.

    This function renders individual calculation items with Leapfrog-style visual formatting.

    Args:
        item: The item to display (Number, Category, Variable, Filter, etc.).
        theme (str, optional): Visual theme, either "light" or "dark".
            If None, uses the global theme set by set_theme(). Defaults to None.
        colors (dict, optional): Custom color palette to override theme defaults.
            Keys can include: 'background', 'text', 'variable', 'label', 'if',
            'arrow', 'comment', 'var_ref'. Defaults to None.
        display_output (bool): Whether to display output in Jupyter.
            If False, returns HTML string. Defaults to True.

    Returns:
        str or None: If display_output is False, returns HTML string.
            Otherwise displays in Jupyter and returns None.

    Example:
        >>> from pollywog.core import Number
        >>> from pollywog.display import display_item
        >>> n = Number(name="x2", children=["[x] * 2"])
        >>> display_item(n, theme="dark")
    """
    from IPython.display import display, HTML

    palette = get_color_palette(theme, colors)
    html_out = (
        f'<div style="font-family:sans-serif;max-width:900px;color:{palette["text"]};">'
    )
    html_out += render_item(item, palette)
    html_out += "</div>"
    
    if display_output:
        display(HTML(html_out))
    else:
        return html_out


def display_calcset(calcset, theme=None, colors=None, display_output=True):
    """
    Display a CalcSet in a Jupyter notebook with Leapfrog-style visual formatting.

    This function renders calculation sets with visual styling similar to Leapfrog,
    making equations and logic blocks easy to read and understand.

    Args:
        calcset (CalcSet): The calculation set to display.
        theme (str, optional): Visual theme, either "light" or "dark".
            If None, uses the global theme set by set_theme(). Defaults to None.
        colors (dict, optional): Custom color palette to override theme defaults.
            Keys can include: 'background', 'text', 'variable', 'label', 'if',
            'arrow', 'comment', 'var_ref'. Defaults to None.
        display_output (bool): Whether to display output in Jupyter.
            If False, returns HTML string. Defaults to True.

    Returns:
        str or None: If display_output is False, returns HTML string.
            Otherwise displays in Jupyter and returns None.

    Example:
        >>> from pollywog.core import CalcSet, Number
        >>> from pollywog.display import display_calcset
        >>> cs = CalcSet([Number(name="x2", children=["[x] * 2"])])
        >>> display_calcset(cs, theme="dark")
    """
    from IPython.display import display, HTML

    palette = get_color_palette(theme, colors)

    def section(title, items):
        if not items:
            return ""
        html_items = "".join(render_item(item, palette) for item in items)
        return f'<details open><summary style="font-size:1.1em;font-weight:bold;color:{palette["variable"]};">{title}</summary>{html_items}</details>'

    variables = [
        i for i in calcset.items if getattr(i, "item_type", None) == "variable"
    ]
    calculations = [
        i for i in calcset.items if getattr(i, "item_type", None) == "calculation"
    ]
    filters = [i for i in calcset.items if getattr(i, "item_type", None) == "filter"]

    html_out = (
        f'<div style="font-family:sans-serif;max-width:900px;color:{palette["text"]};">'
    )
    html_out += section("Variables", variables)
    html_out += section("Calculations", calculations)
    html_out += section("Filters", filters)
    html_out += "</div>"
    
    if display_output:
        display(HTML(html_out))
    else:
        return html_out
