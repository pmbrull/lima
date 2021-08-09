"""
Main module to configure and run lima
"""
import builtins
import os
from typing import Optional

from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.python import PythonLexer
from levy.config import Config

from lima._types import PromptCfg
from lima.evaluator import Evaluator
from lima.bindings import bindings


class Prompt(PromptSession):
    """
    Custom prompt_toolkit Session
    """

    def __init__(self, *args, cfg_file: Optional[str] = None, **kwargs):
        """
        cfg attribute uses levy to configure the prompt.

        :param cfg_file: File to use to load config for the prompt
        """

        if not cfg_file:
            cfg_file = os.path.join(
                os.path.dirname(__file__), "resources", "config.yaml"
            )

        self.cfg = Config.read_file(cfg_file, datatype=PromptCfg)

        kwargs.setdefault("multiline", True)
        kwargs.setdefault("key_bindings", bindings)

        super().__init__(*args, **kwargs)


def main():

    session = Prompt(lexer=PygmentsLexer(PythonLexer))

    _globals = {
        "__name__": "__main__",
        "__package__": None,
        "__doc__": None,
        "__builtins__": builtins,
    }

    evaluator = Evaluator(_globals=_globals, _locals=_globals)

    while True:
        try:
            text = session.prompt("lima> ")
            if text in session.cfg.end_text:
                break

        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        else:
            try:
                res = evaluator.eval(text)
                if res:
                    print_formatted_text(res)
            except Exception as e:
                print_formatted_text(f"{e.__class__.__name__}: {e}")

    print_formatted_text("Bye!")


if __name__ == "__main__":
    main()
