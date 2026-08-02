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

    TO = "to"

    IF = "if"
    ELSE = "else"
    UNLESS = "unless"

    WHILE = "while"
    UNTIL = "until"
    FOREVER = "forever"

    STOP = "stop"
    SKIP = "skip"

    # IDENTIFIERS
    IDENT = "identifier"

    # LITERALS
    INT = "integer"
    FLOAT = "float"

    # OPERATORS
    EQ = "="

    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"
    MOD = "%"

    POWER = "**"

    NOT = "!"

    EQEQ = "=="
    NEQ = "!="

    LT = "<"
    GT = ">"
    LE = "<="
    GE = ">="

    NLT = "!<"
    NGT = "!>"

    NLE = "!<="
    NGE = "!>="

    LSHIFT = "<<"
    RSHIFT = ">>"

    AND = "&"
    XOR = "^"
    OR = "|"

    LAND = "&&"
    LOR = "||"

    # DELIMITERS
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
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
            TokenKind.TO,
            TokenKind.IF,
            TokenKind.ELSE,
            TokenKind.UNLESS,
            TokenKind.WHILE,
            TokenKind.UNTIL,
            TokenKind.FOREVER,
            TokenKind.STOP,
            TokenKind.SKIP,
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
    def isBooleanLiteral(self) -> bool:
        """
        Returns whether this token kind represents a boolean literal.

        Returns:
            bool: True if this token kind represents a boolean literal,
            otherwise False.
        """
        return self in {
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
            TokenKind.EQ,
            TokenKind.PLUS,
            TokenKind.MINUS,
            TokenKind.MUL,
            TokenKind.DIV,
            TokenKind.MOD,
            TokenKind.POWER,
            TokenKind.NOT,
            TokenKind.EQEQ,
            TokenKind.NEQ,
            TokenKind.LT,
            TokenKind.GT,
            TokenKind.LE,
            TokenKind.GE,
            TokenKind.NLT,
            TokenKind.NGT,
            TokenKind.NLE,
            TokenKind.NGE,
            TokenKind.LSHIFT,
            TokenKind.RSHIFT,
            TokenKind.AND,
            TokenKind.XOR,
            TokenKind.OR,
            TokenKind.LAND,
            TokenKind.LOR,
        }

    @property
    def isDelimiter(self) -> bool:
        """
        Returns whether this token kind represents a delimiter.

        Returns:
            bool: True if this token kind represents a delimiter, otherwise False.
        """
        return self in {
            TokenKind.LPAREN,
            TokenKind.RPAREN,
            TokenKind.LBRACE,
            TokenKind.RBRACE,
            TokenKind.SEMICOLON,
        }

    @property
    def isUnaryOp(self) -> bool:
        """
        Returns whether this token kind may begin a unary expression, per
        `unary ::= ( "-" | "!" ) , unary | primary`.

        Returns:
            bool: True if this token kind is a unary prefix operator, otherwise False.
        """
        return self in {
            TokenKind.MINUS,
            TokenKind.NOT,
        }

    @property
    def isLogicalOrOp(self) -> bool:
        """
        Returns whether this token kind is a logical-or level operator, per
        `logical_or ::= logical_and , { "||" , logical_and }`.

        Returns:
            bool: True if this token kind is a logical-or operator, otherwise False.
        """
        return self in {
            TokenKind.LOR,
        }

    @property
    def isLogicalAndOp(self) -> bool:
        """
        Returns whether this token kind is a logical-and level operator, per
        `logical_and ::= bit_or , { "&&" , bit_or }`.

        Returns:
            bool: True if this token kind is a logical-and operator, otherwise False.
        """
        return self in {
            TokenKind.LAND,
        }

    @property
    def isBitOrOp(self) -> bool:
        """
        Returns whether this token kind is a bitwise-or level operator, per
        `bit_or ::= bit_xor , { "|" , bit_xor }`.

        Returns:
            bool: True if this token kind is a bitwise-or operator, otherwise False.
        """
        return self in {
            TokenKind.OR,
        }

    @property
    def isBitXorOp(self) -> bool:
        """
        Returns whether this token kind is a bitwise-xor level operator, per
        `bit_xor ::= bit_and , { "^" , bit_and }`.

        Returns:
            bool: True if this token kind is a bitwise-xor operator, otherwise False.
        """
        return self in {
            TokenKind.XOR,
        }

    @property
    def isBitAndOp(self) -> bool:
        """
        Returns whether this token kind is a bitwise-and level operator, per
        `bit_and ::= equality , { "&" , equality }`.

        Returns:
            bool: True if this token kind is a bitwise-and operator, otherwise False.
        """
        return self in {
            TokenKind.AND,
        }

    @property
    def isEqualityOp(self) -> bool:
        """
        Returns whether this token kind is an equality level operator, per
        `equality ::= relational , { ( "==" | "!=" ) , relational }`.

        Returns:
            bool: True if this token kind is an equality operator, otherwise False.
        """
        return self in {
            TokenKind.EQEQ,
            TokenKind.NEQ,
        }

    @property
    def isRelationalOp(self) -> bool:
        """
        Returns whether this token kind is a relational level operator, per
        `relational ::= shift , { ( "<" | ">" | "<=" | ">=" | "!<" | "!>" | "!<=" | "!>=" ) , shift }`.

        Returns:
            bool: True if this token kind is a relational operator, otherwise False.
        """
        return self in {
            TokenKind.LT,
            TokenKind.GT,
            TokenKind.LE,
            TokenKind.GE,
            TokenKind.NLT,
            TokenKind.NGT,
            TokenKind.NLE,
            TokenKind.NGE,
        }

    @property
    def isShiftOp(self) -> bool:
        """
        Returns whether this token kind is a shift level operator, per
        `shift ::= cast , { ( "<<" | ">>" ) , cast }`.

        Returns:
            bool: True if this token kind is a shift operator, otherwise False.
        """
        return self in {
            TokenKind.LSHIFT,
            TokenKind.RSHIFT,
        }

    @property
    def isAdditiveOp(self) -> bool:
        """
        Returns whether this token kind is an additive level operator, per
        `additive ::= multiplicative , { ( "+" | "-" ) , multiplicative }`.

        Returns:
            bool: True if this token kind is an additive operator, otherwise False.
        """
        return self in {
            TokenKind.PLUS,
            TokenKind.MINUS,
        }

    @property
    def isMultiplicativeOp(self) -> bool:
        """
        Returns whether this token kind is a multiplicative level operator, per
        `multiplicative ::= power , { ( "*" | "/" | "%" ) , power }`.

        Returns:
            bool: True if this token kind is a multiplicative operator, otherwise False.
        """
        return self in {
            TokenKind.MUL,
            TokenKind.DIV,
            TokenKind.MOD,
        }

    @property
    def isPowerOp(self) -> bool:
        """
        Returns whether this token kind is a power level operator, per
        `power ::= unary , { "**" , unary }`.

        Returns:
            bool: True if this token kind is a power operator, otherwise False.
        """
        return self in {
            TokenKind.POWER,
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
