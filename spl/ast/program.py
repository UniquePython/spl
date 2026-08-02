from __future__ import annotations

from dataclasses import dataclass

from spl.ast.stmt import Statement
from spl.span import Span


@dataclass(frozen=True, slots=True)
class Program:
    """The root node: an entire parsed source file."""

    statements: tuple[Statement, ...]
    span: Span
