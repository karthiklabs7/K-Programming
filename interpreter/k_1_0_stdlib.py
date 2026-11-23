"""K 1.0 standard library utilities."""

import math


class KStdLibError(Exception):
    pass


def k_type(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "map"
    return "object"


def k_number(value):
    try:
        return float(value) if "." in str(value) else int(value)
    except (ValueError, TypeError):
        raise KStdLibError(f"Cannot convert to number: {value}")


def k_string(value):
    return str(value)


def k_boolean(value):
    return bool(value)


def k_range(*args):
    try:
        return list(range(*args))
    except (TypeError, ValueError) as error:
        raise KStdLibError(str(error)) from error


def k_min(values):
    try:
        return min(values)
    except (TypeError, ValueError) as error:
        raise KStdLibError(str(error)) from error


def k_max(values):
    try:
        return max(values)
    except (TypeError, ValueError) as error:
        raise KStdLibError(str(error)) from error


def k_sum(values):
    try:
        return sum(values)
    except (TypeError, ValueError) as error:
        raise KStdLibError(str(error)) from error


def k_sorted(values):
    try:
        return sorted(values)
    except TypeError as error:
        raise KStdLibError(str(error)) from error


def k_abs(value):
    try:
        return abs(value)
    except TypeError as error:
        raise KStdLibError(str(error)) from error


def k_round(value, digits=0):
    try:
        return round(value, digits)
    except TypeError as error:
        raise KStdLibError(str(error)) from error


def k_sqrt(value):
    try:
        result = math.sqrt(value)
        return int(result) if result.is_integer() else result
    except (ValueError, TypeError) as error:
        raise KStdLibError(str(error)) from error


def k_power(base, exponent):
    try:
        return base ** exponent
    except (ValueError, TypeError, OverflowError) as error:
        raise KStdLibError(str(error)) from error


def k_floor(value):
    try:
        return math.floor(value)
    except (ValueError, TypeError) as error:
        raise KStdLibError(str(error)) from error


def k_ceil(value):
    try:
        return math.ceil(value)
    except (ValueError, TypeError) as error:
        raise KStdLibError(str(error)) from error


K_STDLIB = {
    "type": k_type,
    "number": k_number,
    "string": k_string,
    "boolean": k_boolean,
    "range": k_range,
    "min": k_min,
    "max": k_max,
    "sum": k_sum,
    "sorted": k_sorted,
    "abs": k_abs,
    "round": k_round,
    "sqrt": k_sqrt,
    "pow": k_power,
    "floor": k_floor,
    "ceil": k_ceil,
}
