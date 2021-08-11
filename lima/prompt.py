import os
from typing import Optional

from prompt_toolkit import PromptSession, print_formatted_text, HTML
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.python import PythonLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from levy.config import Config

from lima._types import PromptCfg
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

        self.prompt_num = 1

        kwargs.setdefault("multiline", True)
        kwargs.setdefault("key_bindings", bindings)
        kwargs.setdefault("lexer", PygmentsLexer(PythonLexer))
        kwargs.setdefault("style", self.parse_style())

        super().__init__(*args, **kwargs)

    def parse_style(self):
        """
        Parse the style from Config
        """

        style_dict = {k.replace("_", "."): v for k, v in self.cfg.style._vars.items()}

        return Style.from_dict(style_dict)

    def prompt_input(self):
        """
        Display the input line
        """

        return self.prompt(
            f"[{self.prompt_num}]: ",
            complete_while_typing=True,
            auto_suggest=AutoSuggestFromHistory(),
        )

    def print(self, res: str) -> None:
        """
        Print result and increase prompt number
        """

        print_formatted_text(f"  >> {res}\n")
        self.prompt_num += 1

    def print_exc(self, exc: Exception) -> None:
        """
        Print exception and increase prompt number
        """

        print_formatted_text(
            f"Out [{self.prompt_num}]: {exc.__class__.__name__}: {exc}\n"
        )
        self.prompt_num += 1

    @staticmethod
    def bye():
        """
        Print Bye message
        """
        print_formatted_text(HTML("<skyblue><b>Bye!</b></skyblue>"))
