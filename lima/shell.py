"""
Main module to configure and run lima
"""
import builtins

from prompt_toolkit import print_formatted_text

from lima.evaluator import Evaluator
from lima.prompt import Prompt


def main():

    session = Prompt()

    _globals = {
        "__name__": "__main__",
        "__package__": None,
        "__doc__": None,
        "__builtins__": builtins,
    }

    evaluator = Evaluator(_globals=_globals, _locals=_globals)

    while True:
        try:
            text = session.prompt_input()

            if text in session.cfg.end_text:
                break

        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        else:
            try:
                if res := evaluator.eval(text):
                    session.print(res)

            except Exception as e:
                session.print_exc(e)

    print_formatted_text("Bye!")


if __name__ == "__main__":
    main()
