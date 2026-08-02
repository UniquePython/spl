from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from spl.ast.expr import Expr
from spl.ast.types import TypeNode
from spl.span import Span


class Mutability(Enum):
    """Whether a declared binding may be reassigned after initialization."""

    CONST = "const"
    MUT = "mut"


@dataclass(frozen=True, slots=True)
class Block:
    """A brace-delimited sequence of statements."""

    statements: tuple[Statement, ...]
    span: Span


@dataclass(frozen=True, slots=True)
class Declaration:
    """A binding declaration: `const/mut name type = expr;`."""

    mutability: Mutability
    name: str
    type: TypeNode
    value: Expr
    span: Span


@dataclass(frozen=True, slots=True)
class Assignment:
    """Reassignment of an existing binding: `name = expr;`."""

    name: str
    value: Expr
    span: Span


@dataclass(frozen=True, slots=True)
class IfStmt:
    """An `if` statement, with an optional `else` branch."""

    condition: Expr
    body: Block
    else_branch: IfStmt | UnlessStmt | Block | None
    span: Span


@dataclass(frozen=True, slots=True)
class UnlessStmt:
    """An `unless` statement, with an optional `else` branch."""

    condition: Expr
    body: Block
    else_branch: IfStmt | UnlessStmt | Block | None
    span: Span


@dataclass(frozen=True, slots=True)
class WhileStmt:
    """A `while` loop."""

    condition: Expr
    body: Block
    span: Span


@dataclass(frozen=True, slots=True)
class UntilStmt:
    """An `until` loop."""

    condition: Expr
    body: Block
    span: Span


@dataclass(frozen=True, slots=True)
class ForeverStmt:
    """A `forever` loop."""

    body: Block
    span: Span


class LoopControlKind(Enum):
    """Which loop-control keyword a `LoopControl` statement represents."""

    STOP = "stop"
    SKIP = "skip"


@dataclass(frozen=True, slots=True)
class LoopControl:
    """A `stop;` or `skip;` statement."""

    kind: LoopControlKind
    span: Span


type Statement = (
    Declaration
    | Assignment
    | IfStmt
    | UnlessStmt
    | WhileStmt
    | UntilStmt
    | ForeverStmt
    | LoopControl
)
