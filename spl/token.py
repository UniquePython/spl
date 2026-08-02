from dataclasses import dataclass

from spl.span import Span
from spl.tokenkind import TokenKind


@dataclass(slots=True, frozen=True)
class Token:
    """Represents a lexical token produced by the lexer."""

    kind: TokenKind  # The lexical category of this token.
    lexeme: str  # The source text corresponding to this token.
    span: Span  # The location of this token in the source code.

    def __str__(self) -> str:
        """
        Returns the string representation of this token.

        Returns:
            str: The string representation of this token.
        """
        return f"{self.kind} ({self.lexeme!r}) @ {self.span}"

    def __repr__(self) -> str:
        """
        Returns the official string representation of this token.

        Returns:
            str: The official string representation of this token.
        """
        return f"Token(kind={self.kind!r}, lexeme={self.lexeme!r}, span={self.span!r})"
