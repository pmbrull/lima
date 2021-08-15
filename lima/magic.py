"""
Magic functions registry
"""
from collections import namedtuple
from textwrap import dedent
from typing import Optional


class InvalidMagicException(Exception):
    """
    Raised if we try to run a magic function that is not in the registry
    """


def register():
    """
    Helps us register custom magic
    """
    registry = dict()

    def add(name: str = None):
        def inner(fn):
            _name = fn.__name__ if not name else name
            registry[_name] = fn
            return fn

        return inner

    Register = namedtuple("Register", ["add", "registry"])
    return Register(add, registry)


magic_registry = register()


@magic_registry.add()
def timeit(statement: str) -> Optional[str]:
    """
    Time the statement to run
    """
    if not statement:
        return "print('An statement is required')"

    run = dedent(
        f"""
        from time import perf_counter
        _t1 = perf_counter()
        res = {statement}
        _t2 = perf_counter()
        print("Elapsed time:", _t2 - _t1)
        del perf_counter, _t1, _t2, res
        """
    )

    return run


@magic_registry.add()
def whoami(_):
    """
    Return path, interpreter and git information
    """
    run = dedent(
        """
        # Check path
        import os
        from pathlib import Path
        path = Path(os.getcwd())
        where = os.path.join("~", path.parent.name, path.name)
        # Check git
        ref = None
        if os.path.exists(".git"):
            with open(".git/HEAD") as head:
                ref = head.readline().split(' ')[-1].strip().replace("refs/heads/", "")
        # Check Python version
        import sys
        version = sys.version.split(' ')[0]
        from prompt_toolkit import HTML, PromptSession, print_formatted_text
        res = f"{where} {'(' + ref + ')' if ref else ''} -V {version}"
        print_formatted_text(HTML(f"<skyblue>{res}</skyblue>"))
        """
    )

    return run
