from __future__ import annotations

from dataclasses import dataclass

from spl.ast.types import TypeNode
from spl.span import Span
from spl.tokenkind import TokenKind


@dataclass(frozen=True, slots=True)
class IntLiteral:
    """An integer literal. Type is not yet resolved at this stage."""

    value: int
    span: Span


@dataclass(frozen=True, slots=True)
class FloatLiteral:
    """A floating-point literal. Type is not yet resolved at this stage."""

    value: float
    span: Span


@dataclass(frozen=True, slots=True)
class BoolLiteral:
    """A boolean literal (`true` or `false`)."""

    value: bool
    span: Span


@dataclass(frozen=True, slots=True)
class Identifier:
    """A reference to a named binding."""

    name: str
    span: Span


@dataclass(frozen=True, slots=True)
class UnaryOp:
    """A unary prefix operation: `-expr` or `!expr`."""

    op: TokenKind  # TokenKind.MINUS | TokenKind.NOT
    operand: Expr
    span: Span


@dataclass(frozen=True, slots=True)
class BinaryOp:
    """
    A binary infix operation, covering every precedence level in the
    expression grammar (logical, bitwise, equality, relational, shift,
    additive, multiplicative, power). Precedence is resolved by the parser;
    this single node shape is used for all of them.
    """

    left: Expr
    op: TokenKind
    right: Expr
    span: Span


@dataclass(frozen=True, slots=True)
class Cast:
    """An explicit type cast: `expr to type`."""

    operand: Expr
    target: TypeNode
    span: Span


type Expr = (
    IntLiteral | FloatLiteral | BoolLiteral | Identifier | UnaryOp | BinaryOp | Cast
)
