import pytest
from .parser import Parser
from .parser import Value as ParserValue
from .lexer import Value as LexerValue


def test_empty_json():
    json = ""
    assert not Parser(json).ast


def test_value():
    json = [LexerValue().BOOLEAN("true")]
    assert Parser(json).ast.value == "true"
    json = [LexerValue().NUMBER("42")]
    assert Parser(json).ast.value == "42"
    json = [LexerValue().STRING("foobar")]
    assert Parser(json).ast.value == "foobar"
    json = [LexerValue().NULL()]
    assert isinstance(Parser(json).ast, ParserValue().NULL)


def test_obj_or_arr_empty():
    json = [LexerValue().BRACKET_LEFT(), LexerValue().BRACKET_RIGHT()]
    assert len(Parser(json).ast.values) == 0
    json = [LexerValue().BRACE_LEFT(), LexerValue().BRACE_RIGHT()]
    assert len(Parser(json).ast.properties) == 0


def test_obj_or_arr_one_value():
    json = [
        LexerValue().BRACKET_LEFT(),
        LexerValue().NUMBER("42"),
        LexerValue().BRACKET_RIGHT(),
    ]
    assert Parser(json).ast.values[0].value == "42"
    json = [
        LexerValue().BRACE_LEFT(),
        LexerValue().STRING("foobar"),
        LexerValue().COLON(),
        LexerValue().NUMBER("42"),
        LexerValue().BRACE_RIGHT(),
    ]
    prop = Parser(json).ast.properties[0]
    assert prop.key.value == "foobar" and prop.value.value == "42"


def test_obj_or_arr_multiple_values():
    json = [
        LexerValue().BRACKET_LEFT(),
        LexerValue().NUMBER("42"),
        LexerValue().COMMA(),
        LexerValue().NUMBER("42"),
        LexerValue().COMMA(),
        LexerValue().NUMBER("42"),
        LexerValue().BRACKET_RIGHT(),
    ]
    assert list(map(lambda v: v.value, Parser(json).ast.values)) == ["42", "42", "42"]
    json = [
        LexerValue().BRACE_LEFT(),
        LexerValue().STRING("foobar"),
        LexerValue().COLON(),
        LexerValue().NUMBER("42"),
        LexerValue().COMMA(),
        LexerValue().STRING("foobar"),
        LexerValue().COLON(),
        LexerValue().NUMBER("42"),
        LexerValue().COMMA(),
        LexerValue().STRING("foobar"),
        LexerValue().COLON(),
        LexerValue().NUMBER("42"),
        LexerValue().BRACE_RIGHT(),
    ]
    assert all(
        list(
            map(
                lambda p: p.key.value == "foobar" and p.value.value == "42",
                Parser(json).ast.properties,
            )
        )
    )


def test_obj_or_arr_not_closed():
    json = [LexerValue().BRACKET_LEFT(), LexerValue().NUMBER("42")]
    with pytest.raises(Exception):
        Parser(json)
    json = [
        LexerValue().BRACE_LEFT(),
        LexerValue().STRING("foobar"),
        LexerValue().COLON(),
        LexerValue().NUMBER("42"),
    ]
    with pytest.raises(Exception):
        Parser(json)


def test_obj_or_arr_trailing_comma():
    json = [
        LexerValue().BRACKET_LEFT(),
        LexerValue().NUMBER("42"),
        LexerValue().COMMA(),
        LexerValue().BRACKET_RIGHT(),
    ]
    with pytest.raises(Exception):
        Parser(json)
    json = [
        LexerValue().BRACE_LEFT(),
        LexerValue().STRING("foobar"),
        LexerValue().COLON(),
        LexerValue().NUMBER("42"),
        LexerValue().COMMA(),
        LexerValue().BRACE_RIGHT(),
    ]
    with pytest.raises(Exception):
        Parser(json)


def test_obj_wrong_key():
    json = [
        LexerValue().BRACE_LEFT(),
        LexerValue().NUMBER("42"),
        LexerValue().COLON(),
        LexerValue().NUMBER("42"),
        LexerValue().BRACE_RIGHT(),
    ]
    with pytest.raises(Exception):
        Parser(json)
