from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.sql import SqlLexer

from levy.config import Config


class Prompt(PromptSession):
    """
    Custom prompt_toolkit Session
    """

    def __init__(self, *args, cfg_file: str = "config.yaml", **kwargs):
        self.cfg = Config.read_file(cfg_file)

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
