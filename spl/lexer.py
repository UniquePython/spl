import string

from spl.errors import LexerError
from spl.source import Source
from spl.span import Span
from spl.token import Token
from spl.tokenkind import TokenKind

KEYWORDS = {
    # Mutability
    "const": TokenKind.CONST,
    "mut": TokenKind.MUT,
    # Primitive types
    "i8": TokenKind.I8,
    "i16": TokenKind.I16,
    "i32": TokenKind.I32,
    "i64": TokenKind.I64,
    "u8": TokenKind.U8,
    "u16": TokenKind.U16,
    "u32": TokenKind.U32,
    "u64": TokenKind.U64,
    "f32": TokenKind.F32,
    "f64": TokenKind.F64,
    "bool": TokenKind.BOOL,
    # Boolean literals
    "true": TokenKind.TRUE,
    "false": TokenKind.FALSE,
    # Casting
    "to": TokenKind.TO,
    # Conditional statements
    "if": TokenKind.IF,
    "else": TokenKind.ELSE,
    "unless": TokenKind.UNLESS,
    # Looping
    "while": TokenKind.WHILE,
    "until": TokenKind.UNTIL,
    "forever": TokenKind.FOREVER,
    "stop": TokenKind.STOP,
    "skip": TokenKind.SKIP,
}

OPERATORS = {
    "=": TokenKind.EQ,
    "+": TokenKind.PLUS,
    "-": TokenKind.MINUS,
    "*": TokenKind.MUL,
    "/": TokenKind.DIV,
    "%": TokenKind.MOD,
    "**": TokenKind.POWER,
    "!": TokenKind.NOT,
    "==": TokenKind.EQEQ,
    "!=": TokenKind.NEQ,
    "<": TokenKind.LT,
    ">": TokenKind.GT,
    "<=": TokenKind.LE,
    ">=": TokenKind.GE,
    "!<": TokenKind.NLT,
    "!>": TokenKind.NGT,
    "!<=": TokenKind.NLE,
    "!>=": TokenKind.NGE,
    "<<": TokenKind.LSHIFT,
    ">>": TokenKind.RSHIFT,
    "&": TokenKind.AND,
    "^": TokenKind.XOR,
    "|": TokenKind.OR,
    "&&": TokenKind.LAND,
    "||": TokenKind.LOR,
    "(": TokenKind.LPAREN,
    ")": TokenKind.RPAREN,
    "{": TokenKind.LBRACE,
    "}": TokenKind.RBRACE,
    ";": TokenKind.SEMICOLON,
}

LONGEST_FIRST_OPERATORS = tuple(
    sorted(OPERATORS.items(), key=lambda item: len(item[0]), reverse=True)
)

IDENT_START = frozenset(string.ascii_letters)
IDENT_REMAINING = frozenset(string.ascii_letters + string.digits + "_")

DIGITS = frozenset(string.digits)


class Lexer:
    def __init__(self, source: Source) -> None:
        """Initializes a new lexer for the given source code.

        Args:
            source (Source): The source code to tokenize.
        """
        self.source = source
        self.code = self.source.code
        self.length = len(self.code)

        self.pos = 0

    def eof(self) -> bool:
        """Checks whether the lexer has reached the end of the source code.

        Returns:
            bool: True if the lexer is at the end of the source code, otherwise False.
        """
        return self.pos >= self.length

    def peek(self, offset: int = 0) -> str | None:
        """Returns the character at the current position plus an offset without advancing.

        Args:
            offset (int, optional): The number of characters to look ahead. Defaults to 0.

        Returns:
            str | None: The character at the requested position, or None if it is out of bounds.
        """
        pos = self.pos + offset

        if pos >= self.length:
            return None

        return self.code[pos]

    def advance(self) -> str | None:
        """Consumes the current character and advances the lexer position.

        Returns:
            str | None: The consumed character, or None if the lexer is at the end of the source.
        """
        ch = self.peek()

        if ch is not None:
            self.pos += 1

        return ch

    def match(self, expected: str) -> bool:
        """Consumes the current character if it matches the expected character.

        Args:
            expected (str): The character to match against.

        Returns:
            bool: True if the character matched and was consumed, otherwise False.
        """
        if self.peek() != expected:
            return False

        self.advance()
        return True

    def newToken(self, kind: TokenKind, start: int) -> Token:
        """Creates a new token spanning from the given start position to the current position.

        Args:
            kind (TokenKind): The kind of token to create.
            start (int): The starting position of the token.

        Returns:
            Token: The newly created token.
        """
        return Token(kind, self.code[start : self.pos], Span(start, self.pos))

    def skipWhitespace(self) -> None:
        """Advances the lexer past all consecutive whitespace characters."""
        while (ch := self.peek()) is not None and ch.isspace():
            self.advance()

    def lexIdentifier(self) -> Token:
        """Lexes an identifier or keyword from the source code.

        Returns:
            Token: The token representing the identifier or keyword.
        """
        start = self.pos

        self.advance()

        while (ch := self.peek()) is not None:
            if ch in IDENT_REMAINING:
                self.advance()
            else:
                break

        text = self.code[start : self.pos]
        kind = KEYWORDS.get(text, TokenKind.IDENT)

        return self.newToken(kind, start)

    def lexNumber(self) -> Token:
        """Lexes an integer or floating-point literal from the source code.

        Returns:
            Token: The token representing the numeric literal.
        """
        start = self.pos

        while (ch := self.peek()) is not None and ch in DIGITS:
            self.advance()

        if self.peek() == "." and self.peek(1) in DIGITS:
            self.advance()

            while (ch := self.peek()) is not None and ch in DIGITS:
                self.advance()

            return self.newToken(TokenKind.FLOAT, start)

        return self.newToken(TokenKind.INT, start)

    def lexOperator(self) -> Token:
        """Lexes an operator or delimiter from the source code.

        Raises:
            LexerError: If an unexpected character is encountered.

        Returns:
            Token: The token representing the operator or delimiter.
        """
        start = self.pos

        for operator, kind in LONGEST_FIRST_OPERATORS:
            if self.code.startswith(operator, self.pos):
                self.pos += len(operator)
                return self.newToken(kind, start)

        raise LexerError(
            self.source,
            Span(self.pos, self.pos + 1),
            f"unexpected character {self.peek()!r}",
        )

    def lex(self) -> list[Token]:
        """Lexes the entire source code into a list of tokens.

        Raises:
            LexerError: If an unexpected character is encountered.

        Returns:
            list[Token]: The list of tokens produced by the lexer.
        """
        tokens: list[Token] = []

        while not self.eof():
            self.skipWhitespace()

            if self.eof():
                break

            ch = self.peek()

            if ch in IDENT_START:
                tokens.append(self.lexIdentifier())

            elif ch in DIGITS:
                tokens.append(self.lexNumber())

            else:
                tokens.append(self.lexOperator())

        tokens.append(Token(TokenKind.EOF, "", Span(self.pos, self.pos)))

        return tokens
