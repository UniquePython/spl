from collections.abc import Callable

from spl.ast import (
    Assignment,
    BinaryOp,
    Block,
    BoolLiteral,
    Cast,
    Declaration,
    Expr,
    FloatLiteral,
    ForeverStmt,
    Identifier,
    IfStmt,
    IntLiteral,
    LoopControl,
    LoopControlKind,
    Mutability,
    Program,
    Statement,
    TypeNode,
    UnaryOp,
    UnlessStmt,
    UntilStmt,
    WhileStmt,
)
from spl.errors import ParserError
from spl.source import Source
from spl.span import Span
from spl.token import Token
from spl.tokenkind import TokenKind


class Parser:
    """
    A recursive descent parser that consumes a token stream and produces an
    AST conforming to the grammar in `grammar`. The method structure mirrors
    the grammar's productions directly, so the grammar file should be read
    alongside this module.
    """

    def __init__(self, source: Source, tokens: list[Token]) -> None:
        """
        Initializes a new parser for the given token stream.

        Args:
            source: The source the tokens were lexed from (used for error
                reporting).
            tokens: The full token stream, including a trailing EOF token.
        """
        self.source = source
        self.tokens = tokens
        self.pos = 0

    # -- Token stream helpers -------------------------------------------

    def peek(self, offset: int = 0) -> Token:
        """
        Returns the token at the current position plus an offset without
        advancing. Reading past the end of the stream returns the EOF token.

        Args:
            offset: The number of tokens to look ahead.

        Returns:
            Token: The token at the requested position.
        """
        pos = self.pos + offset

        if pos >= len(self.tokens):
            return self.tokens[-1]  # EOF

        return self.tokens[pos]

    def advance(self) -> Token:
        """
        Consumes the current token and advances the parser position.

        Returns:
            Token: The consumed token.
        """
        token = self.peek()

        if not token.kind.isEOF:
            self.pos += 1

        return token

    def check(self, *kinds: TokenKind) -> bool:
        """
        Checks whether the current token matches one of the given kinds,
        without consuming it.

        Args:
            kinds: The token kinds to check against.

        Returns:
            bool: True if the current token's kind is one of `kinds`.
        """
        return self.peek().kind in kinds

    def match(self, *kinds: TokenKind) -> Token | None:
        """
        Consumes the current token if it matches one of the given kinds.

        Args:
            kinds: The token kinds to match against.

        Returns:
            Token | None: The consumed token if it matched, otherwise None.
        """
        if not self.check(*kinds):
            return None

        return self.advance()

    def matchPred(self, predicate: Callable[[TokenKind], bool]) -> Token | None:
        """
        Consumes the current token if its kind satisfies the given
        predicate (typically a TokenKind classification property, e.g.
        `lambda kind: kind.isRelationalOp`).

        Args:
            predicate: A predicate over TokenKind.

        Returns:
            Token | None: The consumed token if it matched, otherwise None.
        """
        current = self.peek()

        if not predicate(current.kind):
            return None

        return self.advance()

    def expect(self, kind: TokenKind) -> Token:
        """
        Consumes the current token if it matches the given kind, otherwise
        raises a ParserError.

        Args:
            kind: The token kind required at this position.

        Raises:
            ParserError: If the current token does not match `kind`.

        Returns:
            Token: The consumed token.
        """
        token = self.match(kind)

        if token is None:
            current = self.peek()
            raise ParserError(self.source, current.span, [kind], current.kind)

        return token

    def errorHere(self, expected: "list[TokenKind] | str") -> ParserError:
        """
        Builds a ParserError positioned at the current token, without
        raising it.

        Args:
            expected: The expected token kinds, or a description of what
                was expected.

        Returns:
            ParserError: The constructed error.
        """
        current = self.peek()
        return ParserError(self.source, current.span, expected, current.kind)

    def spanFrom(self, start: Token) -> Span:
        """
        Builds a span covering from the start of `start` to the end of the
        most recently consumed token.

        Args:
            start: The token the span should begin at.

        Returns:
            Span: The resulting span.
        """
        end = self.tokens[self.pos - 1].span.end if self.pos > 0 else start.span.end
        return Span(start.span.start, end)

    # -- Program ----------------------------------------------------------

    def parseProgram(self) -> Program:
        """
        Parses an entire token stream as a program.

        Returns:
            Program: The parsed program.
        """
        start = self.peek()
        statements: list[Statement] = []

        while not self.check(TokenKind.EOF):
            statements.append(self.parseStatement())

        return Program(tuple(statements), self.spanFrom(start))

    # -- Statements ---------------------------------------------------------

    def parseStatement(self) -> Statement:
        """
        Parses a single statement, dispatching on the current token's kind.

        Raises:
            ParserError: If the current token does not begin any valid
                statement.

        Returns:
            Statement: The parsed statement.
        """
        kind = self.peek().kind

        if kind in (TokenKind.CONST, TokenKind.MUT):
            return self.parseDeclaration()

        if kind is TokenKind.IDENT:
            return self.parseAssignment()

        if kind is TokenKind.IF:
            return self.parseIfStmt()

        if kind is TokenKind.UNLESS:
            return self.parseUnlessStmt()

        if kind is TokenKind.WHILE:
            return self.parseWhileStmt()

        if kind is TokenKind.UNTIL:
            return self.parseUntilStmt()

        if kind is TokenKind.FOREVER:
            return self.parseForeverStmt()

        if kind in (TokenKind.STOP, TokenKind.SKIP):
            return self.parseLoopControl()

        raise self.errorHere("a statement")

    def parseBlock(self) -> Block:
        """
        Parses a brace-delimited sequence of statements.

        Returns:
            Block: The parsed block.
        """
        start = self.expect(TokenKind.LBRACE)
        statements: list[Statement] = []

        while not self.check(TokenKind.RBRACE):
            statements.append(self.parseStatement())

        self.expect(TokenKind.RBRACE)

        return Block(tuple(statements), self.spanFrom(start))

    def parseMutability(self) -> Mutability:
        """
        Parses a mutability keyword (`const` or `mut`).

        Raises:
            ParserError: If the current token is not a mutability keyword.

        Returns:
            Mutability: The parsed mutability.
        """
        token = self.match(TokenKind.CONST, TokenKind.MUT)

        if token is None:
            raise self.errorHere([TokenKind.CONST, TokenKind.MUT])

        return Mutability.CONST if token.kind is TokenKind.CONST else Mutability.MUT

    def parseTypeNode(self) -> TypeNode:
        """
        Parses a type annotation.

        Raises:
            ParserError: If the current token is not a built-in type
                keyword.

        Returns:
            TypeNode: The parsed type annotation.
        """
        token = self.matchPred(lambda kind: kind.isType)

        if token is None:
            raise self.errorHere("a type")

        return TypeNode(token.kind, token.span)

    def parseDeclaration(self) -> Declaration:
        """
        Parses a declaration: `mutability identifier type "=" expression ";"`.

        Returns:
            Declaration: The parsed declaration.
        """
        start = self.peek()

        mutability = self.parseMutability()
        name = self.expect(TokenKind.IDENT)
        typeNode = self.parseTypeNode()
        self.expect(TokenKind.EQ)
        value = self.parseExpression()
        self.expect(TokenKind.SEMICOLON)

        return Declaration(
            mutability, name.lexeme, typeNode, value, self.spanFrom(start)
        )

    def parseAssignment(self) -> Assignment:
        """
        Parses an assignment: `identifier "=" expression ";"`.

        Returns:
            Assignment: The parsed assignment.
        """
        start = self.peek()

        name = self.expect(TokenKind.IDENT)
        self.expect(TokenKind.EQ)
        value = self.parseExpression()
        self.expect(TokenKind.SEMICOLON)

        return Assignment(name.lexeme, value, self.spanFrom(start))

    def parseIfStmt(self) -> IfStmt:
        """
        Parses an `if` statement, including an optional `else` branch.

        Returns:
            IfStmt: The parsed if statement.
        """
        start = self.expect(TokenKind.IF)
        condition = self.parseExpression()
        body = self.parseBlock()
        elseBranch = self.parseElseBranch()

        return IfStmt(condition, body, elseBranch, self.spanFrom(start))

    def parseUnlessStmt(self) -> UnlessStmt:
        """
        Parses an `unless` statement, including an optional `else` branch.

        Returns:
            UnlessStmt: The parsed unless statement.
        """
        start = self.expect(TokenKind.UNLESS)
        condition = self.parseExpression()
        body = self.parseBlock()
        elseBranch = self.parseElseBranch()

        return UnlessStmt(condition, body, elseBranch, self.spanFrom(start))

    def parseElseBranch(self) -> "IfStmt | UnlessStmt | Block | None":
        """
        Parses an optional `else` clause, per
        `[ "else" , ( if_stmt | unless_stmt | block ) ]`.

        Returns:
            IfStmt | UnlessStmt | Block | None: The parsed else branch, or
            None if no `else` clause is present.
        """
        if self.match(TokenKind.ELSE) is None:
            return None

        if self.check(TokenKind.IF):
            return self.parseIfStmt()

        if self.check(TokenKind.UNLESS):
            return self.parseUnlessStmt()

        return self.parseBlock()

    def parseWhileStmt(self) -> WhileStmt:
        """
        Parses a `while` loop.

        Returns:
            WhileStmt: The parsed while statement.
        """
        start = self.expect(TokenKind.WHILE)
        condition = self.parseExpression()
        body = self.parseBlock()

        return WhileStmt(condition, body, self.spanFrom(start))

    def parseUntilStmt(self) -> UntilStmt:
        """
        Parses an `until` loop.

        Returns:
            UntilStmt: The parsed until statement.
        """
        start = self.expect(TokenKind.UNTIL)
        condition = self.parseExpression()
        body = self.parseBlock()

        return UntilStmt(condition, body, self.spanFrom(start))

    def parseForeverStmt(self) -> ForeverStmt:
        """
        Parses a `forever` loop.

        Returns:
            ForeverStmt: The parsed forever statement.
        """
        start = self.expect(TokenKind.FOREVER)
        body = self.parseBlock()

        return ForeverStmt(body, self.spanFrom(start))

    def parseLoopControl(self) -> LoopControl:
        """
        Parses a `stop;` or `skip;` statement.

        Returns:
            LoopControl: The parsed loop control statement.
        """
        start = self.peek()
        token = self.match(TokenKind.STOP, TokenKind.SKIP)

        if token is None:
            raise self.errorHere([TokenKind.STOP, TokenKind.SKIP])

        self.expect(TokenKind.SEMICOLON)

        kind = (
            LoopControlKind.STOP
            if token.kind is TokenKind.STOP
            else LoopControlKind.SKIP
        )

        return LoopControl(kind, self.spanFrom(start))

    # -- Expressions: binary precedence chain --------------------------

    def parseBinaryLevel(
        self, isOp: Callable[[TokenKind], bool], nextLevel: Callable[[], Expr]
    ) -> Expr:
        """
        Parses a single left-associative binary precedence level, shared by
        every level of the form `level ::= nextLevel , { op , nextLevel }`.

        Args:
            isOp: A TokenKind predicate recognizing this level's operators
                (typically a TokenKind classification property, e.g.
                `lambda kind: kind.isRelationalOp`).
            nextLevel: The parse method for the next-higher-precedence
                level.

        Returns:
            Expr: The parsed expression, left-associatively folded if more
            than one operator was consumed.
        """
        start = self.peek()
        left = nextLevel()

        while True:
            op = self.matchPred(isOp)

            if op is None:
                break

            right = nextLevel()
            left = BinaryOp(left, op.kind, right, self.spanFrom(start))

        return left

    def parseExpression(self) -> Expr:
        """
        Parses an expression: `expression ::= logical_or`.

        Returns:
            Expr: The parsed expression.
        """
        return self.parseLogicalOr()

    def parseLogicalOr(self) -> Expr:
        return self.parseBinaryLevel(
            lambda kind: kind.isLogicalOrOp, self.parseLogicalAnd
        )

    def parseLogicalAnd(self) -> Expr:
        return self.parseBinaryLevel(lambda kind: kind.isLogicalAndOp, self.parseBitOr)

    def parseBitOr(self) -> Expr:
        return self.parseBinaryLevel(lambda kind: kind.isBitOrOp, self.parseBitXor)

    def parseBitXor(self) -> Expr:
        return self.parseBinaryLevel(lambda kind: kind.isBitXorOp, self.parseBitAnd)

    def parseBitAnd(self) -> Expr:
        return self.parseBinaryLevel(lambda kind: kind.isBitAndOp, self.parseEquality)

    def parseEquality(self) -> Expr:
        return self.parseBinaryLevel(
            lambda kind: kind.isEqualityOp, self.parseRelational
        )

    def parseRelational(self) -> Expr:
        return self.parseBinaryLevel(lambda kind: kind.isRelationalOp, self.parseShift)

    def parseShift(self) -> Expr:
        return self.parseBinaryLevel(lambda kind: kind.isShiftOp, self.parseCast)

    def parseCast(self) -> Expr:
        """
        Parses a cast expression: `cast ::= additive , { "to" , type }`.

        Returns:
            Expr: The parsed expression, wrapped in a Cast node for each
            `to type` suffix encountered.
        """
        start = self.peek()
        expr = self.parseAdditive()

        while self.match(TokenKind.TO) is not None:
            target = self.parseTypeNode()
            expr = Cast(expr, target, self.spanFrom(start))

        return expr

    def parseAdditive(self) -> Expr:
        return self.parseBinaryLevel(
            lambda kind: kind.isAdditiveOp, self.parseMultiplicative
        )

    def parseMultiplicative(self) -> Expr:
        return self.parseBinaryLevel(
            lambda kind: kind.isMultiplicativeOp, self.parsePower
        )

    def parsePower(self) -> Expr:
        # NOTE: the grammar defines power as left-associative
        # (`power ::= unary , { "**" , unary }`), not the conventional
        # right-associative behavior of `**` in most languages. This is
        # intentional per project decision, not an oversight.
        return self.parseBinaryLevel(lambda kind: kind.isPowerOp, self.parseUnary)

    def parseUnary(self) -> Expr:
        """
        Parses a unary expression: `unary ::= ( "-" | "!" ) , unary | primary`.

        Returns:
            Expr: The parsed expression.
        """
        start = self.peek()
        op = self.matchPred(lambda kind: kind.isUnaryOp)

        if op is not None:
            operand = self.parseUnary()
            return UnaryOp(op.kind, operand, self.spanFrom(start))

        return self.parsePrimary()

    def parsePrimary(self) -> Expr:
        """
        Parses a primary expression: a literal, identifier, or
        parenthesized expression.

        Raises:
            ParserError: If the current token does not begin a valid
                primary expression.

        Returns:
            Expr: The parsed expression. Parentheses are resolved away;
            no Grouping node is produced.
        """
        if self.check(TokenKind.INT):
            token = self.advance()
            return IntLiteral(int(token.lexeme), token.span)

        if self.check(TokenKind.FLOAT):
            token = self.advance()
            return FloatLiteral(float(token.lexeme), token.span)

        if self.check(TokenKind.TRUE, TokenKind.FALSE):
            token = self.advance()
            return BoolLiteral(token.kind is TokenKind.TRUE, token.span)

        if self.check(TokenKind.IDENT):
            token = self.advance()
            return Identifier(token.lexeme, token.span)

        if self.match(TokenKind.LPAREN) is not None:
            expr = self.parseExpression()
            self.expect(TokenKind.RPAREN)
            return expr

        raise self.errorHere("an expression")
