# tests/test_interpreter.py
import pytest
from lexer import Lexer
from parse import Parser
from interpreter import Interpreter
from errors import LexerError, ParseError, InterpreterError


def run(code):
    output_lines = []
    symbol_table_state = []

    def on_error(msg):
        raise InterpreterError(msg)

    def on_output(text):
        output_lines.append(str(text))

    def on_symbol_update(table):
        symbol_table_state.clear()
        symbol_table_state.extend(table)

    lex = Lexer(code, on_error=on_error)
    tokens = lex.tokenize()

    parser = Parser(tokens, on_error=on_error)
    parser.program()
    assert parser.checkErr() == 1, "Code failed parsing — fix your test input"

    interp = Interpreter(
        tokens,
        on_error=on_error,
        on_output=on_output,
        on_input=lambda prompt: "42",
        on_symbol_update=on_symbol_update,
    )
    interp.program()

    return {"output": "".join(output_lines), "symbol_table": symbol_table_state}


def get_var(symbol_table, name):
    for entry in symbol_table:
        if entry[0] == name:
            return entry[1]
    return None


##############################################################################
# OUTPUT
##############################################################################


def test_visible_string():
    result = run('HAI\nVISIBLE "hello"\nKTHXBYE\n')
    assert "hello" in result["output"]


def test_visible_integer():
    result = run("HAI\nVISIBLE 42\nKTHXBYE\n")
    assert "42" in result["output"]


def test_visible_variable():
    result = run("HAI\nI HAS A x ITZ 99\nVISIBLE x\nKTHXBYE\n")
    assert "99" in result["output"]


##############################################################################
# VARIABLES
##############################################################################


def test_variable_declaration_uninitialized():
    result = run("HAI\nI HAS A x\nKTHXBYE\n")
    assert get_var(result["symbol_table"], "x") == "NO VALUE"


def test_variable_declaration_with_integer():
    result = run("HAI\nI HAS A x ITZ 7\nKTHXBYE\n")
    assert get_var(result["symbol_table"], "x") == "7"


def test_variable_declaration_with_string():
    result = run('HAI\nI HAS A x ITZ "hello"\nKTHXBYE\n')
    assert get_var(result["symbol_table"], "x") == '"hello"'


def test_variable_assignment():
    result = run("HAI\nI HAS A x ITZ 1\nx R 99\nKTHXBYE\n")
    assert get_var(result["symbol_table"], "x") == "99"


def test_uninitialized_variable_raises_error():
    with pytest.raises(InterpreterError):
        run("HAI\nI HAS A x\nVISIBLE x\nKTHXBYE\n")


##############################################################################
# ARITHMETIC
##############################################################################


def test_sum_of():
    result = run("HAI\nI HAS A x ITZ SUM OF 3 AN 4\nVISIBLE x\nKTHXBYE\n")
    assert "7" in result["output"]


def test_diff_of():
    result = run("HAI\nI HAS A x ITZ DIFF OF 10 AN 3\nVISIBLE x\nKTHXBYE\n")
    assert "7" in result["output"]


def test_produkt_of():
    result = run("HAI\nI HAS A x ITZ PRODUKT OF 3 AN 4\nVISIBLE x\nKTHXBYE\n")
    assert "12" in result["output"]


def test_quoshunt_of():
    result = run("HAI\nI HAS A x ITZ QUOSHUNT OF 10 AN 2\nVISIBLE x\nKTHXBYE\n")
    assert "5" in result["output"]


def test_mod_of():
    result = run("HAI\nI HAS A x ITZ MOD OF 10 AN 3\nVISIBLE x\nKTHXBYE\n")
    assert "1" in result["output"]


def test_biggr_of():
    result = run("HAI\nI HAS A x ITZ BIGGR OF 3 AN 7\nVISIBLE x\nKTHXBYE\n")
    assert "7" in result["output"]


def test_smallr_of():
    result = run("HAI\nI HAS A x ITZ SMALLR OF 3 AN 7\nVISIBLE x\nKTHXBYE\n")
    assert "3" in result["output"]


##############################################################################
# BOOLEAN
##############################################################################


def test_both_of_win_win():
    result = run("HAI\nBOTH OF WIN AN WIN\nVISIBLE IT\nKTHXBYE\n")
    assert "WIN" in result["output"]


def test_both_of_win_fail():
    result = run("HAI\nBOTH OF WIN AN FAIL\nVISIBLE IT\nKTHXBYE\n")
    assert "FAIL" in result["output"]


def test_either_of_fail_fail():
    result = run("HAI\nEITHER OF FAIL AN FAIL\nVISIBLE IT\nKTHXBYE\n")
    assert "FAIL" in result["output"]


def test_not_win():
    result = run("HAI\nNOT WIN\nVISIBLE IT\nKTHXBYE\n")
    assert "FAIL" in result["output"]


##############################################################################
# COMPARISON
##############################################################################


def test_both_saem_equal_values():
    result = run("HAI\nBOTH SAEM 5 AN 5\nVISIBLE IT\nKTHXBYE\n")
    assert "WIN" in result["output"]


def test_both_saem_unequal_values():
    result = run("HAI\nBOTH SAEM 5 AN 6\nVISIBLE IT\nKTHXBYE\n")
    assert "FAIL" in result["output"]


def test_diffrint_unequal_values():
    result = run("HAI\nDIFFRINT 5 AN 6\nVISIBLE IT\nKTHXBYE\n")
    assert "WIN" in result["output"]


##############################################################################
# CONDITIONALS
##############################################################################


def test_if_then_executes_ya_rly():
    code = (
        "HAI\n"
        "BOTH SAEM 1 AN 1\n"
        "O RLY?\n"
        "  YA RLY\n"
        '    VISIBLE "yes"\n'
        "  NO WAI\n"
        '    VISIBLE "no"\n'
        "OIC\n"
        "KTHXBYE\n"
    )
    result = run(code)
    assert "yes" in result["output"]
    assert "no" not in result["output"]


def test_if_then_executes_no_wai():
    code = (
        "HAI\n"
        "BOTH SAEM 1 AN 2\n"
        "O RLY?\n"
        "  YA RLY\n"
        '    VISIBLE "yes"\n'
        "  NO WAI\n"
        '    VISIBLE "no"\n'
        "OIC\n"
        "KTHXBYE\n"
    )
    result = run(code)
    assert "no" in result["output"]
    assert "yes" not in result["output"]


##############################################################################
# INPUT
##############################################################################


def test_gimmeh_stores_value():
    result = run("HAI\nI HAS A x\nGIMMEH x\nKTHXBYE\n")
    assert get_var(result["symbol_table"], "x") == "42"
