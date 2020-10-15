import pytest

from .lexer import Lexer


def test_null():
    json = "null"
    got = list(Lexer(json))[0]
    assert isinstance(got, Value().NULL)


def test_brace_left():
    json = "{"
    got = list(Lexer(json))[0]
    assert isinstance(got, Value().BRACE_LEFT)


def test_brace_right():
    json = "}"
    got = list(Lexer(json))[0]
    assert isinstance(got, Value().BRACE_RIGHT)


def test_bracket_left():
    json = "["
    got = list(Lexer(json))[0]
    assert isinstance(got, Value().BRACKET_LEFT)


def test_bracket_right():
    json = "]"
    got = list(Lexer(json))[0]
    assert isinstance(got, Value().BRACKET_RIGHT)


def test_colon():
    json = ":"
    got = list(Lexer(json))[0]
    assert isinstance(got, Value().COLON)


def test_comma():
    json = ","
    got = list(Lexer(json))[0]
    assert isinstance(got, Value().COMMA)


@pytest.mark.parametrize(
    "string, want",
    [
        ('""', ""),
        ('"hello world"', "hello world"),
        ('"fÜck ☺ \t it"', "fÜck ☺ \t it"),
        ('"\\\t\r"', "\\\t\r"),
    ],
)
def test_string_pass(string, want):
    got = list(Lexer(string))[0].value
    assert got == want


@pytest.mark.parametrize("string", ['"',])
def test_string_fail(string):
    with pytest.raises(Exception):
        list(Lexer(string))


@pytest.mark.parametrize("number", ["42", "69.420", "1e9", "42.69e-98", "-0", "-9e-8"])
def test_number_pass(number):
    got = list(Lexer(number))[0].value
    assert got == number


@pytest.mark.parametrize("number", ["-", "69e420.1", "e9", "1e",])
def test_number_fail(number):
    with pytest.raises(Exception):
        list(Lexer(number))


@pytest.mark.parametrize("boolean", ["true", "false"])
def test_boolean_pass(boolean):
    got = list(Lexer(boolean))[0]
    assert isinstance(got, Value().BOOLEAN)


@pytest.mark.parametrize("boolean", ["True", "fAlse", "TRUE"])
def test_boolean_fail(boolean):
    with pytest.raises(Exception):
        list(Lexer(boolean))
