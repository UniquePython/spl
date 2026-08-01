from spl.source import Source
from spl.span import Span


class InternalError(Exception):
    """
    Raised when the compiler encounters an unexpected internal state.

    This exception indicates a bug in the compiler rather than an error in the
    user's source code.
    """

    def __init__(self, message: str) -> None:
        super().__init__(f"Internal error: {message}")


class LexerError(Exception):
    """
    Raised when the lexer encounters an invalid or unexpected sequence of
    characters in the source code.
    """

    def __init__(self, source: Source, span: Span, message: str) -> None:
        """
        Initializes a new lexer error.

        Args:
            source: The source being lexed.
            span: The span at which the error occurred.
            message: A description of the error.
        """
        self.source = source
        self.span = span
        self.message = message

        super().__init__(message)
