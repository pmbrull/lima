from typing import Iterable

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document


def get_jedi_script_from_document(document, _locals, _globals):
    import jedi  # We keep this import in-line, to improve start-up time.

    # Importing Jedi is 'slow'.

    try:
        return jedi.Interpreter(
            code=document.text,
            namespaces=[_locals, _globals],
        )
    except ValueError:
        # Invalid cursor position.
        # ValueError('`column` parameter is not in a valid range.')
        return None
    except AttributeError:
        # Workaround for #65: https://github.com/jonathanslenders/python-prompt-toolkit/issues/65
        # See also: https://github.com/davidhalter/jedi/issues/508
        return None
    except IndexError:
        # Workaround Jedi issue #514: for https://github.com/davidhalter/jedi/issues/514
        return None
    except KeyError:
        # Workaroud for a crash when the input is "u'", the start of a unicode string.
        return None
    except Exception:
        # Workaround for: https://github.com/jonathanslenders/ptpython/issues/91
        return None


class LimaCompleter(Completer):
    """
    Completer for Python code.
    """

    def __init__(
        self,
        _globals: dict,
        _locals: dict,
    ) -> None:
        super().__init__()

        self._globals = _globals
        self._locals = _locals

        self._jedi_completer = JediCompleter(self._globals, self._locals)

    def _complete_python_while_typing(self, document: Document) -> bool:
        """
        When `complete_while_typing` is set, only return completions when this
        returns `True`.
        """
        text = document.text_before_cursor  # .rstrip()
        char_before_cursor = text[-1:]
        return bool(
            text and (char_before_cursor.isalnum() or char_before_cursor in "_.([,")
        )

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        """
        Get Python completions.
        """

        # Do Jedi completions.
        if complete_event.completion_requested or self._complete_python_while_typing(
            document
        ):
            yield from self._jedi_completer.get_completions(document, complete_event)


class JediCompleter(Completer):
    """
    Autocompleter that uses the Jedi library.
    """

    def __init__(self, _globals, _locals) -> None:
        super().__init__()

        self._globals = _globals
        self._locals = _locals

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        script = get_jedi_script_from_document(document, self._locals, self._globals)

        if script:
            try:
                jedi_completions = script.complete(
                    column=document.cursor_position_col,
                    line=document.cursor_position_row + 1,
                )
            except TypeError:
                # Issue #9: bad syntax causes completions() to fail in jedi.
                # https://github.com/jonathanslenders/python-prompt-toolkit/issues/9
                pass
            except UnicodeDecodeError:
                # Issue #43: UnicodeDecodeError on OpenBSD
                # https://github.com/jonathanslenders/python-prompt-toolkit/issues/43
                pass
            except AttributeError:
                # Jedi issue #513: https://github.com/davidhalter/jedi/issues/513
                pass
            except ValueError:
                # Jedi issue: "ValueError: invalid \x escape"
                pass
            except KeyError:
                # Jedi issue: "KeyError: u'a_lambda'."
                # https://github.com/jonathanslenders/ptpython/issues/89
                pass
            except IOError:
                # Jedi issue: "IOError: No such file or directory."
                # https://github.com/jonathanslenders/ptpython/issues/71
                pass
            except AssertionError:
                # In jedi.parser.__init__.py: 227, in remove_last_newline,
                # the assertion "newline.value.endswith('\n')" can fail.
                pass
            except SystemError:
                # In jedi.api.helpers.py: 144, in get_stack_at_position
                # raise SystemError("This really shouldn't happen. There's a bug in Jedi.")
                pass
            except NotImplementedError:
                # See: https://github.com/jonathanslenders/ptpython/issues/223
                pass
            except Exception:
                # Supress all other Jedi exceptions.
                pass
            else:
                # Move function parameters to the top.
                jedi_completions = sorted(
                    jedi_completions,
                    key=lambda jc: (
                        # Params first.
                        jc.type != "param",
                        # Private at the end.
                        jc.name.startswith("_"),
                        # Then sort by name.
                        jc.name_with_symbols.lower(),
                    ),
                )

                for jc in jedi_completions:
                    if jc.type == "function":
                        suffix = "()"
                    else:
                        suffix = ""

                    if jc.type == "param":
                        suffix = "..."

                    yield Completion(
                        jc.name_with_symbols,
                        len(jc.complete) - len(jc.name_with_symbols),
                        display=jc.name_with_symbols + suffix,
                        display_meta=jc.type,
                        # style=_get_style_for_jedi_completion(jc),
                    )
