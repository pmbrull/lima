"""
Magic functions registry
"""
from collections import namedtuple
from textwrap import dedent


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
def timeit(statement: str) -> str:
    """
    Time the statement to run
    """
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
