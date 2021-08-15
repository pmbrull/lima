"""
Multiline helpers.

Ported from ptpython.utils and changed and simplified pieces of logic.
"""
import re

from prompt_toolkit.application.current import get_app
from prompt_toolkit.filters import Condition

UNINDENT_KW = ["pass", "continue", "break", "return", "raise"]
_multiline_string_delims = re.compile("[']{3}|[\"]{3}")


def unclosed_brackets(text: str) -> bool:
    """
    Starting at the end of the string. If we find an opening bracket
    for which we didn't had a closing one yet, return True.
    """
    stack = []

    # Ignore braces inside strings
    text = re.sub(r"""('[^']*'|"[^"]*")""", "", text)

    for char in reversed(text):
        if char in "])}":
            stack.append(char)

        elif char in "[({":
            if stack:
                if (
                    (char == "[" and stack[-1] == "]")
                    or (char == "{" and stack[-1] == "}")
                    or (char == "(" and stack[-1] == ")")
                ):
                    stack.pop()
            else:
                # Opening bracket for which we didn't had a closing one.
                return True

    return False


def unclosed_multiline_string(text: str) -> bool:
    """
    True if we have a multiline string that needs to be closed.
    We can check if we need to close if the length of the
    found delimiters for a specific char (" | ') is odd.

    E.g., we have: '''random.
    """

    delimiters = _multiline_string_delims.findall(text)

    return bool(
        len([d for d in delimiters if d == '"' * 3]) % 2
        | len([d for d in delimiters if d == "'" * 3]) % 2
    )


def document_is_multiline_python(document) -> bool:
    """
    Determine whether this is a multiline Python document.
    """

    if (
        "\n" in document.text  # We have a line jump
        or document.text_before_cursor[-1:] == "\\"  # New line char
        or unclosed_multiline_string(document.text)
    ):
        return True

    if (
        document.current_line.rstrip()[-1:] == ":"
        or (
            document.is_cursor_at_the_end
            and unclosed_brackets(document.text_before_cursor)
        )
        or document.text.startswith("@")  # Decorator
    ):
        return True

    return False


def auto_newline(buffer):
    """
    Insert \n at the cursor position. Also add necessary padding.

    Used when in multiline python document.
    """

    insert_text = buffer.insert_text

    if buffer.document.current_line_after_cursor.strip():
        # When we are in the middle of a line. Always insert a newline.
        insert_text("\n")
    else:
        # Go to new line, but also add indentation.
        current_line = buffer.document.current_line_before_cursor.rstrip()
        insert_text("\n")

        # Unident if the last line ends with one of these keywords
        for keyword in UNINDENT_KW:
            begin = current_line.lstrip()
            # e.g., "pass", "return smt"...
            if begin.startswith(keyword + " ") or begin == keyword:
                unindent = True
                break
        else:
            unindent = False
        #
        # Insert the current whitespaces minus 4 if we need to unindent
        current_indent_level = len(current_line) - len(current_line.lstrip())
        next_indent = current_indent_level - 4 if unindent else current_indent_level
        insert_text(" " * next_indent)

        # If the last line ends with a colon, add four extra spaces.
        if current_line[-1] == ":":
            insert_text(" " * 4)


@Condition
def tab_should_insert_whitespace():
    app = get_app()

    buffer = app.current_buffer
    before_cursor = buffer.document.current_line_before_cursor

    return bool(not before_cursor or before_cursor.isspace())
