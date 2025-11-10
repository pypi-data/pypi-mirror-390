__all__ = [
    "StdkitError",
    "InvalidChoiceError",
]

from collections.abc import Sequence
from typing import Any


class StdkitError(Exception):
    """Base exception for all errors raised by stdkit."""

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = self.__class__.__name__
        self.message: str = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r})"


class InvalidChoiceError(StdkitError, ValueError):
    """Raised when a value is not one of an allowed set of choices.

    Examples
    --------
    >>> import stdkit
    >>> err = stdkit.exceptions.InvalidChoiceError(value=0, choices=[1, 2, 3])
    >>> err.message
    'value=0 invalid choice - expected a value from (1, 2, 3)'
    """

    def __init__(self, value: Any, choices: Sequence[Any] | None = None):
        self.value = value
        self.choices = tuple(choices) if choices is not None else None

        message = f"{value=!r} invalid choice"
        if self.choices is not None:
            message += f" - expected a value from {self.choices}"

        super().__init__(message)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(value={self.value!r}, "
            f"choices={self.choices if self.choices is not None else None})"
        )
