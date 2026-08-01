from enum import Enum


class TokenKind(Enum):
    """The set of all token kinds recognized by the lexer."""

    # KEYWORDS
    CONST = "const"
    MUT = "mut"

    # IDENTIFIERS
    IDENT = "identifier"

    # LITERALS
    INT = "integer"

    # OPERATORS
    EQUAL = "="

    # DELIMITERS
    SEMICOLON = ";"

    # SPECIAL
    EOF = "end of file"

    @property
    def isKeyword(self) -> bool:
        """
        Returns whether this token kind represents a language keyword.

        Returns:
            bool: True if this token kind represents a language keyword, otherwise False.
        """
        return self in {
            TokenKind.CONST,
            TokenKind.MUT,
        }

    @property
    def isIdentifier(self) -> bool:
        """
        Returns whether this token kind represents an identifier.

        Returns:
            bool: True if this token kind represents an identifier, otherwise False.
        """
        return self is TokenKind.IDENT

    @property
    def isLiteral(self) -> bool:
        """
        Returns whether this token kind represents a literal.

        Returns:
            bool: True if this token kind represents a literal, otherwise False.
        """
        return self is TokenKind.INT

    @property
    def isOperator(self) -> bool:
        """
        Returns whether this token kind represents an operator.

        Returns:
            bool: True if this token kind represents an operator, otherwise False.
        """
        return self is TokenKind.EQUAL

    @property
    def isDelimiter(self) -> bool:
        """
        Returns whether this token kind represents a delimiter.

        Returns:
            bool: True if this token kind represents a delimiter, otherwise False.
        """
        return self is TokenKind.SEMICOLON

    @property
    def isEOF(self) -> bool:
        """
        Returns whether this token kind represents the end-of-file marker.

        Returns:
            bool: True if this token kind represents the end-of-file marker, otherwise False.
        """
        return self is TokenKind.EOF

    def __str__(self) -> str:
        """
        Returns the string representation of this token kind.

        Returns:
            str: The string representation of this token kind.
        """
        return self.value

    def __repr__(self) -> str:
        """
        Returns the official string representation of this token kind.

        Returns:
            str: The official string representation of this token kind.
        """
        return f"TokenKind.{self.name}"
