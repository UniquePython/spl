from enum import Enum


class TokenKind(Enum):
    """The set of all token kinds recognized by the lexer."""

    # KEYWORDS
    CONST = "const"
    MUT = "mut"

    I8 = "i8"
    I16 = "i16"
    I32 = "i32"
    I64 = "i64"

    U8 = "u8"
    U16 = "u16"
    U32 = "u32"
    U64 = "u64"

    F32 = "f32"
    F64 = "f64"

    BOOL = "bool"

    TRUE = "true"
    FALSE = "false"

    # IDENTIFIERS
    IDENT = "identifier"

    # LITERALS
    INT = "integer"
    FLOAT = "float"

    # OPERATORS
    EQUAL = "="
    MINUS = "-"

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
            TokenKind.I8,
            TokenKind.I16,
            TokenKind.I32,
            TokenKind.I64,
            TokenKind.U8,
            TokenKind.U16,
            TokenKind.U32,
            TokenKind.U64,
            TokenKind.F32,
            TokenKind.F64,
            TokenKind.BOOL,
            TokenKind.TRUE,
            TokenKind.FALSE,
        }

    @property
    def isType(self) -> bool:
        """
        Returns whether this token kind represents a built-in type keyword.

        Returns:
            bool: True if this token kind represents a built-in type keyword,
            otherwise False.
        """
        return self in {
            TokenKind.I8,
            TokenKind.I16,
            TokenKind.I32,
            TokenKind.I64,
            TokenKind.U8,
            TokenKind.U16,
            TokenKind.U32,
            TokenKind.U64,
            TokenKind.F32,
            TokenKind.F64,
            TokenKind.BOOL,
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
        return self in {
            TokenKind.INT,
            TokenKind.FLOAT,
            TokenKind.TRUE,
            TokenKind.FALSE,
        }

    @property
    def isOperator(self) -> bool:
        """
        Returns whether this token kind represents an operator.

        Returns:
            bool: True if this token kind represents an operator, otherwise False.
        """
        return self in {
            TokenKind.EQUAL,
            TokenKind.MINUS,
        }

    @property
    def isDelimiter(self) -> bool:
        """
        Returns whether this token kind represents a delimiter.

        Returns:
            bool: True if this token kind represents a delimiter, otherwise False.
        """
        return self in {
            TokenKind.SEMICOLON,
        }

    @property
    def isEOF(self) -> bool:
        """
        Returns whether this token kind represents the end-of-file marker.

        Returns:
            bool: True if this token kind represents the end-of-file marker,
            otherwise False.
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
