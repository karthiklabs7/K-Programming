"""K 1.0 debugger and error diagnostics."""

from dataclasses import dataclass, field
import traceback


@dataclass
class KDiagnostic:
    message: str
    category: str = "RuntimeError"
    filename: str = "<source>"
    line: int = 1
    column: int = 1
    severity: str = "error"

    def format(self):
        return (
            f"{self.filename}:{self.line}:{self.column}: "
            f"{self.severity} [{self.category}]: {self.message}"
        )


@dataclass
class KDebugLogger:
    enabled: bool = False
    entries: list = field(default_factory=list)

    def log(self, message, level="DEBUG"):
        if self.enabled:
            entry = f"[{level}] {message}"
            self.entries.append(entry)
            return entry
        return None

    def clear(self):
        self.entries.clear()


class KDiagnostics:
    def __init__(self, filename="<source>"):
        self.filename = filename
        self.errors = []

    def report(self, message, category="RuntimeError",
               line=1, column=1, severity="error"):
        diagnostic = KDiagnostic(
            str(message), category, self.filename,
            int(line), int(column), severity
        )
        self.errors.append(diagnostic)
        return diagnostic

    def syntax_error(self, message, line=1, column=1):
        return self.report(message, "SyntaxError", line, column)

    def type_error(self, message, line=1, column=1):
        return self.report(message, "TypeError", line, column)

    def runtime_error(self, message, line=1, column=1):
        return self.report(message, "RuntimeError", line, column)

    def has_errors(self):
        return any(item.severity == "error" for item in self.errors)

    def format_all(self):
        return [item.format() for item in self.errors]

    def clear(self):
        self.errors.clear()


def k_stack_trace(error):
    return "".join(
        traceback.format_exception(
            type(error), error, error.__traceback__
        )
    )


def k_assert(condition, message="K assertion failed"):
    if not condition:
        raise AssertionError(str(message))
    return True


DIAGNOSTIC_BUILTINS = {
    "assert": k_assert,
    "stack_trace": k_stack_trace,
}
