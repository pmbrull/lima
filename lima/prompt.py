"""
Module defining custom Prompt
"""
import os
import sys
from pathlib import Path
from typing import Optional

from levy.config import Config
from prompt_toolkit import HTML, PromptSession, print_formatted_text
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from pygments.lexers.python import PythonLexer

from lima._types import PromptCfg
from lima.bindings import bindings
from lima.completion import LimaCompleter
from lima.evaluator import Evaluator


class Prompt(PromptSession):
    """
    Custom prompt_toolkit Session
    """

    def __init__(
        self,
        *args,
        evaluator: Evaluator,
        cfg_file: Optional[str] = None,
        history_file: Optional[str] = None,
        **kwargs,
    ):
        """
        cfg attribute uses levy to configure the prompt.

        :param cfg_file: File to use to load config for the prompt
        """

        if not cfg_file:
            cfg_file = os.path.join(
                os.path.dirname(__file__), "resources", "config.yaml"
            )

        self.cfg = Config.read_file(cfg_file, datatype=PromptCfg)

        self.evaluator = evaluator
        self.prompt_num = 1

        kwargs.setdefault("multiline", True)
        kwargs.setdefault("key_bindings", bindings)
        kwargs.setdefault("lexer", PygmentsLexer(PythonLexer))
        kwargs.setdefault("style", self.parse_style())
        kwargs.setdefault("history", self.set_history(history_file))
        kwargs.setdefault(
            "completer",
            LimaCompleter(
                _globals=self.evaluator._globals,
                _locals=self.evaluator._locals,
            ),
        )
        kwargs.setdefault("complete_in_thread", True)

        super().__init__(*args, **kwargs)

    def parse_style(self):
        """
        Parse the style from Config
        """

        style_dict = {k.replace("_", "."): v for k, v in self.cfg.style._vars.items()}

        return Style.from_dict(style_dict)

    @staticmethod
    def set_history(file: Optional[str] = None) -> FileHistory:
        """
        Prepare a directory with the history file

        This allows us to have autosuggestions based in history
        between sessions
        """

        basedir = ".pylima"
        name = "history"

        history_file = file or os.path.join(basedir, name)

        if not os.path.exists(basedir):
            os.mkdir(basedir)
        if not os.path.isfile(history_file):
            open(history_file, "w+").close()

        return FileHistory(history_file)

    def prepare_toolbar(self):
        """
        Prepare HTML text to pass to the bottom toolbar.

        It will display the current path, git info and executable.
        """
        path = Path(os.getcwd())
        where = os.path.join("~", path.parent.name, path.name)
        # Check git
        ref = None
        if os.path.exists(".git"):
            with open(".git/HEAD") as head:
                ref = head.readline().split(" ")[-1].strip().replace("refs/heads/", "")
        # Check Python version
        version = sys.version.split(" ")[0]

        color = self.cfg.style("bottom_toolbar_color", "skyblue")
        git_color = self.cfg.style("bottom_toolbar_git_color", "ansigreen")

        color_where = f"<{color}>{where}</{color}>"
        color_git = f"<{git_color}>({ref})</{git_color}>" if ref else ""
        py_ver = f"<right>{sys.executable} -V {version}</right>"

        return HTML(f"<b>{color_where} {color_git} {py_ver}</b>")

    def prompt_input(self):
        """
        Display the input line
        """
        color = self.cfg.prompt.dots

        def continuation(width, line_number, is_soft_wrap):
            # pylint: disable=unused-argument
            dots = " " + "." * (width - 2)
            return HTML(f"<{color}>{dots}</{color}>")

        def bottom_toolbar():
            return self.prepare_toolbar()

        return self.prompt(
            f"[{self.prompt_num}]: ",
            complete_while_typing=True,
            auto_suggest=AutoSuggestFromHistory(),
            prompt_continuation=continuation,
            bottom_toolbar=bottom_toolbar,
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
    def hello():
        """
        Greet and use %whoami magic to print info at startup
        """
        print_formatted_text(HTML("<skyblue><b>>> Pylima</b></skyblue>"))

    @staticmethod
    def bye():
        """
        Print Bye message
        """
        print_formatted_text(HTML("<skyblue><b>Bye!</b></skyblue>"))
