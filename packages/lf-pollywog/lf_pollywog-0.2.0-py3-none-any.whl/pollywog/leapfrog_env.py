"""
Leapfrog-like math and text functions for pollywog expression evaluation.
This module provides all the functions and constants used in LEAPFROG_ENV.
"""

import math
import re
import numpy as np

# Math functions


def log(n, base=10):
    return math.log(n, base)


def ln(n):
    return math.log(n)


def exp(n):
    return math.exp(n)


def sqrt(n):
    return math.sqrt(n)


def abs_(n):
    import builtins

    return builtins.abs(n)


def sin(x):
    return math.sin(x)


def cos(x):
    return math.cos(x)


def tan(x):
    return math.tan(x)


def asin(x):
    return math.asin(x)


def acos(x):
    return math.acos(x)


def atan(x):
    return math.atan(x)


def min_(*args):
    import builtins

    return builtins.min(args)


def max_(*args):
    import builtins

    return builtins.max(args)


def clamp(n, lower, upper=None):
    if upper is not None:
        return max(lower, min(n, upper))
    return max(n, lower)


def round_(n, dp=None):
    if dp is not None:
        return round(n, dp)
    return round(n)


def roundsf(n, sf):
    if n == 0:
        return 0
    from math import log10, floor
    import builtins

    return builtins.round(n, -int(floor(log10(abs_(n)))) + (sf - 1))


def floor_(n):
    return math.floor(n)


def ceiling(n):
    return math.ceil(n)


def truncate(n):
    return int(n)


# Text functions


def concat(*args):
    return "".join(str(a) for a in args)


def startswith(t, prefix):
    return str(t).startswith(prefix)


def endswith(t, suffix):
    return str(t).endswith(suffix)


def contains(t, part):
    return part in str(t)


def like(t, pattern):
    return re.search(pattern, str(t)) is not None


def regexp(t, pattern):
    return re.search(pattern, str(t)) is not None


# Wrappers for Leapfrog naming


def min(*args):
    return min_(*args)


def max(*args):
    return max_(*args)


def round(n, dp=None):
    return round_(n, dp)


def floor(n):
    return floor_(n)


def abs(n):
    return abs_(n)


# Utility


def is_normal(n):
    if n is None:
        return False
    try:
        return isinstance(n, (int, float)) and math.isfinite(n)
    except (TypeError, ValueError):
        return False


LEAPFROG_ENV = {
    "log": log,
    "ln": ln,
    "exp": exp,
    "sqrt": sqrt,
    "abs": abs,
    "pi": math.pi,
    "e": math.e,
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "asin": asin,
    "acos": acos,
    "atan": atan,
    "min": min_,
    "max": max_,
    "clamp": clamp,
    "round": round_,
    "roundsf": roundsf,
    "floor": floor_,
    "ceiling": ceiling,
    "truncate": truncate,
    "concat": concat,
    "startswith": startswith,
    "endswith": endswith,
    "contains": contains,
    "like": like,
    "regexp": regexp,
    "is_normal": is_normal,
}
