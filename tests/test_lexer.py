# tests/test_lexer.py
import pytest
from lexer import Lexer
from errors import LexerError


def make_lexer(code):
    """
    Create a Lexer instance with no GUI dependency.
    Returns the lexer and a list that collects any error messages.
    """
    errors = []
    lex = Lexer(code, on_error=lambda msg: errors.append(msg))
    return lex, errors


def tokenize(code):
    """
    Convenience helper — just give me the tokens for this code.
    Raises LexerError if tokenization fails.
    """
    lex, _ = make_lexer(code)
    return lex.tokenize()


def token_values(code):
    """Return just the token values (the second element of each token pair)."""
    return [t[1] for t in tokenize(code)]


def token_types(code):
    """Return just the token types (the first element of each token pair)."""
    return [t[0] for t in tokenize(code)]


##############################################################################
# BASIC STRUCTURE
##############################################################################


def test_empty_program_tokens():
    """HAI and KTHXBYE should always be present in a valid program."""
    values = token_values("HAI\nKTHXBYE\n")
    assert "HAI" in values
    assert "KTHXBYE" in values


def test_hai_kthxbye_classified_as_code_delimiter():
    """HAI and KTHXBYE should be classified as CODE_DELIMITER."""
    tokens = tokenize("HAI\nKTHXBYE\n")
    delimiter_values = [t[1] for t in tokens if t[0] == "CODE_DELIMITER"]
    assert "HAI" in delimiter_values
    assert "KTHXBYE" in delimiter_values


def test_linebreak_token_present():
    """Every line should produce a LINEBREAK EOL token."""
    tokens = tokenize("HAI\nKTHXBYE\n")
    eol_tokens = [t for t in tokens if t[1] == "EOL"]
    assert len(eol_tokens) >= 2


def test_invalid_token_raises_lexer_error():
    """An unrecognized token should raise LexerError, not silently fail."""
    with pytest.raises(LexerError):
        tokenize("HAI\n@@@@\nKTHXBYE\n")


##############################################################################
# COMMENTS
##############################################################################


def test_btw_comment_removed():
    """BTW inline comments should not produce any tokens."""
    values = token_values("HAI\nBTW this is a comment\nKTHXBYE\n")
    assert "this" not in values
    assert "comment" not in values


def test_obtw_tldr_block_comment_removed():
    """OBTW...TLDR block comments should not produce any tokens."""
    code = "HAI\nOBTW\nthis entire block\nis a comment\nTLDR\nKTHXBYE\n"
    values = token_values(code)
    assert "entire" not in values
    assert "block" not in values


def test_btw_after_statement_removed():
    """BTW after a valid statement should remove the comment but keep the statement."""
    values = token_values('HAI\nVISIBLE "hi" BTW print hi\nKTHXBYE\n')
    assert "VISIBLE" in values
    assert "print" not in values


##############################################################################
# LITERALS
##############################################################################


def test_numbr_literal():
    """Integer literals should be tokenized as NUMBR."""
    types = token_types("HAI\nI HAS A x ITZ 42\nKTHXBYE\n")
    assert "NUMBR" in types


def test_negative_numbr_literal():
    """Negative integers should also be tokenized as NUMBR."""
    types = token_types("HAI\nI HAS A x ITZ -7\nKTHXBYE\n")
    assert "NUMBR" in types


def test_numbar_literal():
    """Floating point literals should be tokenized as NUMBAR."""
    types = token_types("HAI\nI HAS A x ITZ 3.14\nKTHXBYE\n")
    assert "NUMBAR" in types


def test_yarn_literal():
    """String literals in double quotes should be tokenized as YARN."""
    tokens = tokenize('HAI\nVISIBLE "hello world"\nKTHXBYE\n')
    yarn_tokens = [t for t in tokens if t[0] == "YARN"]
    assert len(yarn_tokens) == 1
    assert yarn_tokens[0][1] == '"hello world"'


def test_win_troof_literal():
    """WIN should be tokenized as TROOF."""
    types = token_types("HAI\nI HAS A x ITZ WIN\nKTHXBYE\n")
    assert "TROOF" in types


def test_fail_troof_literal():
    """FAIL should be tokenized as TROOF."""
    types = token_types("HAI\nI HAS A x ITZ FAIL\nKTHXBYE\n")
    assert "TROOF" in types


##############################################################################
# KEYWORDS
##############################################################################


def test_multiword_keyword_i_has_a():
    """'I HAS A' should be a single token, not three separate ones."""
    values = token_values("HAI\nI HAS A x\nKTHXBYE\n")
    assert "I HAS A" in values
    assert values.count("I") == 0
    assert values.count("HAS") == 0
    assert values.count("A") == 0


def test_multiword_keyword_sum_of():
    """'SUM OF' should be a single ARITHMETIC_OP token."""
    tokens = tokenize("HAI\nVISIBLE SUM OF 1 AN 2\nKTHXBYE\n")
    arith_tokens = [t for t in tokens if t[0] == "ARITHMETIC_OP"]
    assert any(t[1] == "SUM OF" for t in arith_tokens)


def test_visible_classified_as_output_key():
    """VISIBLE should be classified as OUTPUT_KEY."""
    types = token_types('HAI\nVISIBLE "hi"\nKTHXBYE\n')
    assert "OUTPUT_KEY" in types


def test_gimmeh_classified_as_input_key():
    """GIMMEH should be classified as INPUT_KEY."""
    types = token_types("HAI\nI HAS A x\nGIMMEH x\nKTHXBYE\n")
    assert "INPUT_KEY" in types


def test_identifier_token():
    """A valid variable name should be tokenized as IDENTIFIER."""
    tokens = tokenize("HAI\nI HAS A myVar\nKTHXBYE\n")
    identifier_tokens = [t for t in tokens if t[0] == "IDENTIFIER"]
    assert any(t[1] == "myVar" for t in identifier_tokens)


def test_keyword_inside_identifier_not_split():
    """
    An identifier like 'visible2' should not be broken up just because
    it contains the keyword 'VISIBLE' inside it. The lexer's placeholder
    strategy should prevent this.
    """
    values = token_values("HAI\nI HAS A visible2\nKTHXBYE\n")
    assert "visible2" in values
