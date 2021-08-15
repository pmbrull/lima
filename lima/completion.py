"""
Taken from ptpython.completer and ptpython.util

Copyright (c) 2015, Jonathan Slenders

All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:
* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.
* Neither the name of the {organization} nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from typing import Iterable

from prompt_toolkit.completion import (
    CompleteEvent,
    Completer,
    Completion,
    FuzzyCompleter,
    WordCompleter,
)
from prompt_toolkit.document import Document

from lima.magic import magic_registry


def get_jedi_script_from_document(document, _locals, _globals):
    """
    Given a document and namespaces, return the completion script
    """
    # We keep this import in-line, to improve start-up time.
    import jedi  # pylint: disable=import-outside-toplevel

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
    except Exception:  # pylint: disable=broad-except
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

        self._jedi_completer = FuzzyCompleter(
            completer=JediCompleter(self._globals, self._locals), enable_fuzzy=True
        )

        self._magic_completer = MagicCompleter()

    @staticmethod
    def _complete_python_while_typing(document: Document) -> bool:
        """
        When `complete_while_typing` is set, only return completions when this
        returns `True`.
        """
        text = document.text_before_cursor
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
        # If the input starts with %, use the magic completer
        if document.text.lstrip().startswith("%"):
            yield from self._magic_completer.get_completions(
                Document(
                    text=document.text[1:], cursor_position=document.cursor_position - 1
                ),
                complete_event,
            )
            return

        # Do Jedi completions
        if complete_event.completion_requested or self._complete_python_while_typing(
            document
        ):
            yield from self._jedi_completer.get_completions(document, complete_event)


class MagicCompleter(WordCompleter):
    """
    Autocomplete with magic registry
    """

    def __init__(self):
        words = list(magic_registry.registry.keys())
        super().__init__(words=words)


class JediCompleter(Completer):
    """
    Autocomplete with Jedi: https://github.com/davidhalter/jedi
    """

    def __init__(self, _globals, _locals) -> None:
        super().__init__()

        self._globals = _globals
        self._locals = _locals

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        # pylint: disable=too-many-branches
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
            except Exception:  # pylint: disable=broad-except
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
                    )
