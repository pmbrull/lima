"""
Class holding the evaluation logic
"""
import ast
import subprocess
from typing import Optional

from lima.magic import InvalidMagicException, magic_registry


class Evaluator:
    """
    Contains methods to evaluate python code, commands and magic
    """

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
        exec(code, self._globals, self._locals)  # pylint: disable=exec-used

        if expr:
            code = compile(ast.Expression(expr.value), self.file, "eval")
            res = eval(code, self._globals, self._locals)  # pylint: disable=eval-used

        return res

    def magic_eval(self, statement: str) -> Optional[str]:
        magic, *rest = statement.split(" ")

        try:
            magic_fn = magic_registry.registry[magic]
        except KeyError:
            raise InvalidMagicException(f"'{magic}' is not a registered magic command")

        return self.py_eval(magic_fn(rest))

    @staticmethod
    def cmd_eval(statement: str) -> None:
        """
        Run any statement being passed to the Evaluator

        Don't raise an exception with non-zero exits
        """
        subprocess.run(statement.split(" "), check=False)
