"""
Main module to configure and run lima
"""
import builtins

from lima.evaluator import Evaluator
from lima.prompt import Prompt


def main():
    """
    Create the prompt session to run the shell
    """

    _globals = {
        "__name__": "__main__",
        "__package__": None,
        "__doc__": None,
        "__builtins__": builtins,
    }

    session = Prompt(evaluator=Evaluator(_globals=_globals, _locals=_globals))

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
                if res := session.evaluator.eval(text):
                    session.print(res)

            except Exception as e:  # pylint: disable=broad-except
                session.print_exc(e)

    session.bye()


if __name__ == "__main__":
    main()
