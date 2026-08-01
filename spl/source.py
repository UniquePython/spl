from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Source:
    """
    Represents a source file to be processed by the compiler.
    """

    path: str  # The path to the source file.
    code: str  # The contents of the source file.
