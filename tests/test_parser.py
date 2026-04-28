# tests/test_parser.py
import pytest
from lexer import Lexer
from parse import Parser
from errors import LexerError, ParseError


def parse(code):
    """
    Lex and then parse the given code.
    Returns the parser instance so tests can check errFlag.
    Raises LexerError or ParseError if something goes wrong.
    """
    lex = Lexer(code, on_error=lambda msg: (_ for _ in ()).throw(LexerError(msg)))
    tokens = lex.tokenize()
    parser = Parser(tokens, on_error=lambda msg: (_ for _ in ()).throw(ParseError(msg)))
    parser.program()
    return parser


def assert_valid(code):
    """Assert that the given code passes parsing."""
    parser = parse(code)
    assert parser.checkErr() == 1, "Expected program to be valid but parser rejected it"


def assert_invalid(code):
    """Assert that the given code fails parsing."""
    with pytest.raises((ParseError, LexerError, Exception)):
        parser = parse(code)
        assert parser.checkErr() == 0


##############################################################################
# BASIC STRUCTURE
##############################################################################


def test_minimal_valid_program():
    """HAI and KTHXBYE alone should be a valid program."""
    assert_valid("HAI\nKTHXBYE\n")


def test_missing_kthxbye_is_invalid():
    """A program without KTHXBYE should fail parsing."""
    assert_invalid('HAI\nVISIBLE "hi"\n')


def test_missing_hai_is_invalid():
    """A program without HAI should fail parsing."""
    assert_invalid('VISIBLE "hi"\nKTHXBYE\n')


##############################################################################
# VARIABLE DECLARATION
##############################################################################


def test_variable_declaration_no_value():
    """I HAS A with no ITZ should be valid."""
    assert_valid("HAI\nI HAS A x\nKTHXBYE\n")


def test_variable_declaration_with_numbr():
    """I HAS A with ITZ and an integer should be valid."""
    assert_valid("HAI\nI HAS A x ITZ 42\nKTHXBYE\n")


def test_variable_declaration_with_yarn():
    """I HAS A with ITZ and a string should be valid."""
    assert_valid('HAI\nI HAS A x ITZ "hello"\nKTHXBYE\n')


def test_variable_assignment():
    """Assigning a value to a variable with R should be valid."""
    assert_valid("HAI\nI HAS A x ITZ 1\nx R 99\nKTHXBYE\n")


##############################################################################
# OUTPUT
##############################################################################


def test_visible_with_string():
    """VISIBLE with a string literal should be valid."""
    assert_valid('HAI\nVISIBLE "hello"\nKTHXBYE\n')


def test_visible_with_numbr():
    """VISIBLE with an integer literal should be valid."""
    assert_valid("HAI\nVISIBLE 42\nKTHXBYE\n")


def test_visible_with_identifier():
    """VISIBLE with a variable name should be valid."""
    assert_valid("HAI\nI HAS A x ITZ 1\nVISIBLE x\nKTHXBYE\n")


##############################################################################
# ARITHMETIC
##############################################################################


def test_sum_of():
    """SUM OF expression should be valid."""
    assert_valid("HAI\nVISIBLE SUM OF 1 AN 2\nKTHXBYE\n")


def test_nested_arithmetic():
    """Nested arithmetic expressions should be valid."""
    assert_valid("HAI\nVISIBLE SUM OF 1 AN DIFF OF 5 AN 3\nKTHXBYE\n")


##############################################################################
# CONDITIONALS
##############################################################################


def test_if_then_with_else():
    """O RLY? with YA RLY and NO WAI should be valid."""
    code = (
        "HAI\n"
        "I HAS A x ITZ WIN\n"
        "x O RLY?\n"
        "  YA RLY\n"
        '    VISIBLE "yes"\n'
        "  NO WAI\n"
        '    VISIBLE "no"\n'
        "OIC\n"
        "KTHXBYE\n"
    )
    assert_valid(code)


def test_if_then_without_else():
    """O RLY? with only YA RLY and no NO WAI should be valid."""
    code = (
        "HAI\n"
        "I HAS A x ITZ WIN\n"
        "x O RLY?\n"
        "  YA RLY\n"
        '    VISIBLE "yes"\n'
        "OIC\n"
        "KTHXBYE\n"
    )
    assert_valid(code)


##############################################################################
# LOOPS
##############################################################################


def test_basic_loop():
    """A basic IM IN YR loop should be valid."""
    code = (
        "HAI\n"
        "I HAS A x ITZ 0\n"
        "IM IN YR loop UPPIN YR x TIL BOTH SAEM x AN 5\n"
        "  VISIBLE x\n"
        "IM OUTTA YR loop\n"
        "KTHXBYE\n"
    )
    assert_valid(code)
