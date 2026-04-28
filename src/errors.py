class LexerError(Exception):
    """Raised when the lexer encounters an unrecognized token."""

    pass


class ParseError(Exception):
    """Raised when the parser encounters invalid syntax."""

    pass


class InterpreterError(Exception):
    """Raised during interpretation when something goes wrong at runtime."""

    pass
