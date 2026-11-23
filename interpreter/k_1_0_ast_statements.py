try:
    from .k_1_0_ast_runtime import Environment, evaluate, KRuntimeError
except ImportError:
    from k_1_0_ast_runtime import Environment, evaluate, KRuntimeError


class KReturn(Exception):
    def __init__(self, value=None):
        self.value = value


class KBreak(Exception):
    pass


class KContinue(Exception):
    pass


class KFunction:
    def __init__(self, params, body, closure, builtins):
        self.params = params
        self.body = body
        self.closure = closure
        self.builtins = builtins

    def __call__(self, *args):
        if len(args) != len(self.params):
            raise KRuntimeError(
                f"Expected {len(self.params)} arguments, got {len(args)}"
            )
        local = Environment(self.closure)
        for name, value in zip(self.params, args):
            local.set(name, value)
        try:
            execute(self.body, local, self.builtins)
        except KReturn as result:
            return result.value
        return None


def field(node, name, default=None):
    if isinstance(node, dict):
        return node.get(name, default)
    data = getattr(node, "fields", None)
    if isinstance(data, dict):
        return data.get(name, default)
    return getattr(node, name, default)


def kind(node):
    return str(field(node, "kind", field(node, "type", ""))).lower()




class KThrown(Exception):
    def __init__(self, value):
        self.value = value
        super().__init__(str(value))


def execute(node, environment=None, builtins=None):
    env = environment or Environment()
    funcs = dict(builtins or {})
    funcs.setdefault("print", print)
    funcs.setdefault("say", print)
    return _execute(node, env, funcs)


def _execute(node, env, funcs):
    k = kind(node)

    if k in ("program", "block"):
        result = None
        for statement in field(node, "body", []):
            result = _execute(statement, env, funcs)
        return result

    if k in ("expressionstatement", "expression_statement"):
        return evaluate(field(node, "expression"), env, funcs)

    if k in ("variabledeclaration", "variable_declaration",
             "vardeclaration", "letdeclaration"):
        name = field(node, "name")
        if not name:
            raise KRuntimeError("Variable declaration needs a name")
        initializer = field(node, "initializer",
                            field(node, "value"))
        value = None if initializer is None else evaluate(
            initializer, env, funcs)
        return env.set(name, value)

    if k == "ifstatement":
        condition = evaluate(field(node, "condition"), env, funcs)
        branch = field(node, "then_branch") if condition else field(
            node, "else_branch")
        if branch is not None:
            return _execute(branch, env, funcs)
        return None

    if k == "whilestatement":
        result = None
        iterations = 0
        while evaluate(field(node, "condition"), env, funcs):
            iterations += 1
            if iterations > 100000:
                raise KRuntimeError("Loop safety limit exceeded")
            try:
                result = _execute(field(node, "body"), env, funcs)
            except KContinue:
                continue
            except KBreak:
                break
        return result

    if k == "returnstatement":
        value = field(node, "value")
        raise KReturn(None if value is None else evaluate(value, env, funcs))

    if k == "breakstatement":
        raise KBreak()

    if k == "continuestatement":
        raise KContinue()

    if k == "functiondeclaration":
        name = field(node, "name")
        params = field(node, "params", [])
        body = field(node, "body")
        if not name or body is None:
            raise KRuntimeError("Invalid function declaration")
        function = KFunction(params, body, env, funcs)
        env.set(name, function)
        return function


    # K_1_0_AST_EXCEPTION_SUPPORT
    if k in ("throwstatement", "throw_statement"):
        value = field(node, "value")
        thrown = None if value is None else evaluate(value, env, funcs)
        raise KThrown(thrown)

    if k in ("trycatchstatement", "try_catch_statement"):
        try_body = field(node, "try_body")
        catch_body = field(node, "catch_body")
        catch_name = field(node, "catch_name")
        try:
            return _execute(try_body, env, funcs)
        except KThrown as error:
            if catch_body is None:
                raise
            if catch_name:
                env.set(catch_name, error.value)
            return _execute(catch_body, env, funcs)

    raise KRuntimeError(f"Unsupported statement: {k or 'unknown'}")
