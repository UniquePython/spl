from __future__ import annotations

from dataclasses import dataclass

from spl.span import Span
from spl.tokenkind import TokenKind


@dataclass(frozen=True, slots=True)
class TypeNode:
    """A type annotation as it appears in source (e.g. `i32`, `bool`)."""

    kind: TokenKind  # One of the eleven built-in type keyword kinds.
    span: Span
