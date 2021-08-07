"""
Class holding the evaluation logic
"""
import ast


class Evaluator:
    def __init__(self, *, _globals, _locals):

        self.file = "<stdin>"
        self._globals = _globals
        self._locals = _locals

    def eval(self, stmt: str):
        """
        Smart evaluation of prompt statements.

        If the statement is an expression, we will `eval` and return the result.
        Otherwise, we will `exec` the statement.

        If the statement contains multiple statements ending in an expression,
        we will `exec` all and `eval` the last one.

        At some point, we might add AST transformer to add glitter
        to the parsed code.
        """
        parsed = ast.parse(stmt)

        expr = None
        res = None

        if parsed.body and isinstance(parsed.body[-1], ast.Expr):
            expr = parsed.body.pop()

        code = compile(parsed, self.file, "exec")
        exec(code, self._globals, self._locals)

        if expr:
            code = compile(ast.Expression(expr.value), self.file, "eval")
            res = eval(code, self._globals, self._locals)

        return res
