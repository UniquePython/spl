class SPLInternalError(Exception):
    """
    Raised when the compiler encounters an unexpected internal state.

    This exception indicates a bug in the compiler rather than an error in the
    user's source code.
    """

    def __init__(self, message: str) -> None:
        super().__init__(f"Internal error: {message}")
