"""Standalone runtime safety helpers for K 1.0."""

class KSafetyError(Exception):
    pass

class KRuntimeSafety:
    def __init__(self, max_depth=100, max_items=100000):
        self.max_depth = max_depth
        self.max_items = max_items

    def validate_value(self, value, depth=0):
        if depth > self.max_depth:
            raise KSafetyError("Maximum nesting depth exceeded")
        if isinstance(value, (str, int, float, bool)) or value is None:
            return True
        if isinstance(value, (list, tuple)):
            if len(value) > self.max_items:
                raise KSafetyError("Maximum collection size exceeded")
            return all(self.validate_value(item, depth + 1) for item in value)
        if isinstance(value, dict):
            if len(value) > self.max_items:
                raise KSafetyError("Maximum collection size exceeded")
            return all(
                self.validate_value(k, depth + 1) and
                self.validate_value(v, depth + 1)
                for k, v in value.items()
            )
        raise KSafetyError("Unsupported runtime value type")

    def check_collection_size(self, value):
        if not isinstance(value, (list, tuple, dict, str)):
            raise KSafetyError("Value is not a supported collection")
        if len(value) > self.max_items:
            raise KSafetyError("Maximum collection size exceeded")
        return True

    def check_type(self, value, expected):
        allowed = {
            "number": (int, float),
            "string": (str,),
            "boolean": (bool,),
            "list": (list,),
            "map": (dict,),
        }
        if expected not in allowed:
            raise KSafetyError("Unknown expected type")
        if expected == "number" and isinstance(value, bool):
            raise KSafetyError("Expected number")
        if not isinstance(value, allowed[expected]):
            raise KSafetyError("Expected " + expected)
        return True
