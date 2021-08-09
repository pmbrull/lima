"""
Class holding the evaluation logic
"""
import ast
import subprocess

from typing import Optional


class Evaluator:
    def __init__(self, *, _globals, _locals):

        self.file = "<stdin>"
        self._globals = _globals
        self._locals = _locals

    def eval(self, text: str) -> Optional[str]:
        """
        Evaluator of the statements that we can get as inputs
        :param text:
        """
        if text.startswith("%"):
            return self.magic_eval(text.lstrip("%"))

        if text.startswith("!"):
            return self.cmd_eval(text.lstrip("!"))

        return self.py_eval(text)

    def py_eval(self, statement: str) -> str:
        """
        Smart evaluation of python prompt statements.

        If the statement is an expression, we will `eval` and return the result.
        Otherwise, we will `exec` the statement.

        If the statement contains multiple statements ending in an expression,
        we will `exec` all and `eval` the last one.

        At some point, we might add AST transformer to add glitter
        to the parsed code.
        """
        parsed = ast.parse(statement)

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

    def magic_eval(self, statement: str):
        pass

    @staticmethod
    def cmd_eval(statement: str) -> None:
        subprocess.run(statement.split(" "))
        return None
