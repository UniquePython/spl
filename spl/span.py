from dataclasses import dataclass

from spl.errors import SPLInternalError


@dataclass(slots=True, frozen=True)
class Span:
    """
    Represents a half-open character range in the source text.

    A span covers the interval [start, end), where `start` is the index of the
    first character included in the span and `end` is the index immediately
    after the last character. Empty spans are represented by `start == end`.
    """

    start: int  # Start position of the token in source code (inclusive)
    end: int  # Start position of the token in source code (exclusive)

    def __post_init__(self) -> None:
        if self.start < 0:
            raise SPLInternalError(
                f"Expected span.start >= 0, got {self.start} instead."
            )

        if self.end < self.start:
            raise SPLInternalError(
                f"Expected span.end >= span.start, got span.start={self.start} and span.end={self.end} instead."
            )
