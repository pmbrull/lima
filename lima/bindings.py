"""
Module to add Key Bindings to the session
"""
from prompt_toolkit.application.current import get_app
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.named_commands import accept_line
from prompt_toolkit.keys import Keys

from lima.multiline import auto_newline, document_is_multiline_python

bindings = KeyBindings()


is_returnable = Condition(lambda: get_app().current_buffer.is_returnable)


@bindings.add(Keys.Enter, filter=is_returnable)
def multiline_enter(event):
    """
    When not in multiline, execute. When in multiline, try to
    intelligently add a newline or execute.
    """
    buffer = event.current_buffer
    document = buffer.document
    multiline_doc = document_is_multiline_python(document)

    text_after_cursor = document.text_after_cursor
    text_before_cursor = document.text_before_cursor

    if (
        not text_after_cursor or text_after_cursor.isspace()
    ) and text_before_cursor.replace(" ", "").endswith("\n"):
        # If we are at the end of the buffer, accept
        accept_line(event)

    elif not multiline_doc:
        # Always accept a single line
        accept_line(event)
    else:
        auto_newline(event.current_buffer)


@bindings.add("{", filter=is_returnable)
def brace_left(event):
    event.current_buffer.insert_text("{")
    event.current_buffer.insert_text("}", move_cursor=False)


@bindings.add("(", filter=is_returnable)
def parent_left(event):
    event.current_buffer.insert_text("(")
    event.current_buffer.insert_text(")", move_cursor=False)


@bindings.add("[", filter=is_returnable)
def bracket_left(event):
    event.current_buffer.insert_text("[")
    event.current_buffer.insert_text("]", move_cursor=False)


@bindings.add('"', filter=is_returnable)
def quote_left(event):
    """
    Add another quote if there is no char after the cursor,
    otherwise write it once.
    """
    buffer = event.current_buffer
    document = buffer.document

    text_after_cursor = document.text_after_cursor

    if not text_after_cursor or text_after_cursor.isspace():
        event.current_buffer.insert_text('"')
        event.current_buffer.insert_text('"', move_cursor=False)
    else:
        event.current_buffer.insert_text('"')


@bindings.add("'", filter=is_returnable)
def single_quote_left(event):
    """
    Add another single quote if there is no char after the cursor,
    otherwise write it once.
    """
    buffer = event.current_buffer
    document = buffer.document

    text_after_cursor = document.text_after_cursor

    if not text_after_cursor or text_after_cursor.isspace():
        event.current_buffer.insert_text("'")
        event.current_buffer.insert_text("'", move_cursor=False)
    else:
        event.current_buffer.insert_text("'")
