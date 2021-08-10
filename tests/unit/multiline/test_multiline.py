from lima.multiline import unclosed_brackets, unclosed_multiline_string


def test_unclosed_braces():
    closed = "{[()]}"
    assert not unclosed_brackets(closed)

    unclosed = "{}([1,2,3,(1, 2)"
    assert unclosed_brackets(unclosed)

    more_unclosed = "[[[[((()))]]"
    assert unclosed_brackets(more_unclosed)


def test_multiline_string():
    not_multiline = "hola"
    assert not unclosed_multiline_string(not_multiline)

    not_multiline_2 = '"random"'
    assert not unclosed_multiline_string(not_multiline_2)

    closed_multiline = '"""random"""'
    assert not unclosed_multiline_string(closed_multiline)

    unclosed_multiline = "'''random"
    assert unclosed_multiline_string(unclosed_multiline)

    another_unclosed_multiline = '"""random'
    assert unclosed_multiline_string(another_unclosed_multiline)
