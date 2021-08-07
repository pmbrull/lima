"""Main module to configure and run lima"""
import os
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.sql import SqlLexer
from levy.config import Config

from lima._types import PromptCfg


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

        super().__init__(*args, **kwargs)


def main():
    session = PromptSession(lexer=PygmentsLexer(SqlLexer))
    prompt = Prompt()

    while True:
        try:
            text = session.prompt("> ")
            if text in prompt.cfg.end_text:
                break

        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        else:
            print("You entered:", text)
    print("GoodBye!")


if __name__ == "__main__":
    main()
