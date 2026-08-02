from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from spl.source import Source

if TYPE_CHECKING:
    from spl.span import Span
    from spl.tokenkind import TokenKind


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


class ParserError(Exception):
    """
    Raised when the parser encounters a token sequence that does not match
    any valid production in the grammar.

    Unlike LexerError, this carries structured expectation data (rather than
    only a free-text message) so that callers can build consistent
    diagnostics or, in the future, more advanced tooling (e.g. suggestions)
    without re-parsing the error message itself.
    """

    def __init__(
        self,
        source: Source,
        span: Span,
        expected: Sequence[TokenKind] | str,
        found: TokenKind,
    ) -> None:
        """
        Initializes a new parser error.

        Args:
            source: The source being parsed.
            span: The span at which the error occurred.
            expected: Either the set of token kinds that would have been
                valid at this point, or a short human-readable description
                of what was expected (used when enumerating token kinds
                would not be meaningful, e.g. "a statement").
            found: The token kind that was actually encountered.
        """
        self.source = source
        self.span = span
        self.expected = expected
        self.found = found

        super().__init__(self._formatMessage())

    def _formatMessage(self) -> str:
        """
        Builds the human-readable message for this error from its
        structured fields.

        Returns:
            str: The formatted error message.
        """
        if isinstance(self.expected, str):
            expectedText = self.expected
        elif len(self.expected) == 1:
            expectedText = str(self.expected[0])
        else:
            expectedText = "one of " + ", ".join(str(kind) for kind in self.expected)

        return f"expected {expectedText}, found {self.found}"
