from collections.abc import Callable

from spl.ast import (
    Assignment,
    BinaryOp,
    Block,
    BoolLiteral,
    Cast,
    Declaration,
    Expr,
    ForeverStmt,
    IfStmt,
    LoopControl,
    Program,
    Statement,
    UnaryOp,
    UnlessStmt,
    UntilStmt,
    WhileStmt,
)
from spl.errors import InternalError
from spl.span import Span
from spl.tokenkind import TokenKind

# A comparison-desugaring function takes the already-desugared left and
# right operands plus the original operator's span, and produces an
# equivalent Expr built only from "<", "<=", "==", "!=", and unary "!".
ComparisonDesugarFn = Callable[[Expr, Expr, Span], Expr]


def _lt(left: Expr, right: Expr, span: Span) -> Expr:
    return BinaryOp(left, TokenKind.LT, right, span)


def _le(left: Expr, right: Expr, span: Span) -> Expr:
    return BinaryOp(left, TokenKind.LE, right, span)


def _negate(inner: Expr, span: Span) -> Expr:
    return UnaryOp(TokenKind.NOT, inner, span)


# Direct table from each non-canonical comparison operator to its
# desugaring, in terms of the original (left, right) operand order. Kept as
# an explicit table rather than a compositional/recursive rewrite (e.g.
# deriving "!>" from ">" from "<") because the set is small and fixed, and
# a flat table is easier to verify against the semantics doc at a glance.
_COMPARISON_DESUGAR: dict[TokenKind, ComparisonDesugarFn] = {
    # a > b   -> b < a
    TokenKind.GT: lambda left, right, span: _lt(right, left, span),
    # a >= b  -> b <= a
    TokenKind.GE: lambda left, right, span: _le(right, left, span),
    # a !< b  -> !(a < b)
    TokenKind.NLT: lambda left, right, span: _negate(_lt(left, right, span), span),
    # a !> b  -> !(b < a)      (i.e. !(a > b), with > already expanded)
    TokenKind.NGT: lambda left, right, span: _negate(_lt(right, left, span), span),
    # a !<= b -> !(a <= b)
    TokenKind.NLE: lambda left, right, span: _negate(_le(left, right, span), span),
    # a !>= b -> !(b <= a)     (i.e. !(a >= b), with >= already expanded)
    TokenKind.NGE: lambda left, right, span: _negate(_le(right, left, span), span),
}


def desugarProgram(program: Program) -> Program:
    """
    Desugars an entire program: rewrites `unless`, `until`, and `forever`
    statements into their `if`/`while` equivalents, and rewrites every
    non-canonical comparison operator (`>`, `>=`, `!<`, `!>`, `!<=`, `!>=`)
    into a form built only from `<`, `<=`, `==`, `!=`, and unary `!`.

    Args:
        program: The parsed program to desugar.

    Returns:
        Program: An equivalent program using only the canonical statement
        and comparison forms.
    """
    return Program(
        tuple(desugarStatement(stmt) for stmt in program.statements),
        program.span,
    )


def desugarStatement(stmt: Statement) -> Statement:
    """
    Desugars a single statement, recursively desugaring any nested
    statements and expressions it contains.

    Args:
        stmt: The statement to desugar.

    Returns:
        Statement: An equivalent statement using only the canonical forms.
        `UnlessStmt` becomes `IfStmt`, `UntilStmt` becomes `WhileStmt`, and
        `ForeverStmt` becomes `WhileStmt` with a `true` condition.
    """
    match stmt:
        case Declaration():
            return Declaration(
                stmt.mutability,
                stmt.name,
                stmt.type,
                desugarExpr(stmt.value),
                stmt.span,
            )

        case Assignment():
            return Assignment(stmt.name, desugarExpr(stmt.value), stmt.span)

        case IfStmt():
            return IfStmt(
                desugarExpr(stmt.condition),
                desugarBlock(stmt.body),
                desugarElseBranch(stmt.else_branch),
                stmt.span,
            )

        case UnlessStmt():
            # `unless cond { body } [else branch]`
            # -> `if !cond { body } [else branch]`
            negatedCondition = UnaryOp(
                TokenKind.NOT, desugarExpr(stmt.condition), stmt.condition.span
            )
            return IfStmt(
                negatedCondition,
                desugarBlock(stmt.body),
                desugarElseBranch(stmt.else_branch),
                stmt.span,
            )

        case WhileStmt():
            return WhileStmt(
                desugarExpr(stmt.condition), desugarBlock(stmt.body), stmt.span
            )

        case UntilStmt():
            # `until cond { body }` -> `while !cond { body }`
            negatedCondition = UnaryOp(
                TokenKind.NOT, desugarExpr(stmt.condition), stmt.condition.span
            )
            return WhileStmt(negatedCondition, desugarBlock(stmt.body), stmt.span)

        case ForeverStmt():
            # `forever { body }` -> `while true { body }`
            trueCondition = BoolLiteral(True, stmt.span)
            return WhileStmt(trueCondition, desugarBlock(stmt.body), stmt.span)

        case LoopControl():
            return stmt


def desugarElseBranch(
    branch: "IfStmt | UnlessStmt | Block | None",
) -> "IfStmt | Block | None":
    """
    Desugars an `else` branch, which may itself be an `if`, an `unless`
    (which becomes an `if` here too), a plain block, or absent.

    Args:
        branch: The else branch to desugar.

    Returns:
        IfStmt | Block | None: The desugared else branch. `UnlessStmt` is
        folded into `IfStmt`, since `unless` no longer exists after
        desugaring.
    """
    if branch is None:
        return None

    if isinstance(branch, Block):
        return desugarBlock(branch)

    # IfStmt | UnlessStmt: desugarStatement already narrows UnlessStmt to
    # IfStmt, so the return type here is always IfStmt.
    desugared = desugarStatement(branch)

    if not isinstance(desugared, IfStmt):
        raise InternalError(
            f"expected desugaring an if/unless else-branch to produce an "
            f"IfStmt, got {type(desugared).__name__} instead"
        )

    return desugared


def desugarBlock(block: Block) -> Block:
    """
    Desugars every statement in a block.

    Args:
        block: The block to desugar.

    Returns:
        Block: An equivalent block with every statement desugared.
    """
    return Block(
        tuple(desugarStatement(inner) for inner in block.statements), block.span
    )


def desugarExpr(expr: Expr) -> Expr:
    """
    Desugars a single expression, recursively desugaring its subexpressions
    and rewriting any non-canonical comparison operator into a form built
    only from `<`, `<=`, `==`, `!=`, and unary `!`.

    Args:
        expr: The expression to desugar.

    Returns:
        Expr: An equivalent expression using only canonical comparison
        operators.
    """
    match expr:
        case BinaryOp():
            left = desugarExpr(expr.left)
            right = desugarExpr(expr.right)

            desugarFn = _COMPARISON_DESUGAR.get(expr.op)
            if desugarFn is not None:
                return desugarFn(left, right, expr.span)

            return BinaryOp(left, expr.op, right, expr.span)

        case UnaryOp():
            return UnaryOp(expr.op, desugarExpr(expr.operand), expr.span)

        case Cast():
            return Cast(desugarExpr(expr.operand), expr.target, expr.span)

        case _:
            # IntLiteral | FloatLiteral | BoolLiteral | Identifier: no
            # subexpressions to recurse into.
            return expr
