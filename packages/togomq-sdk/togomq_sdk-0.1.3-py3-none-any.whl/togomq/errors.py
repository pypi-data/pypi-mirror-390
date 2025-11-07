"""Error handling for TogoMQ SDK."""

from enum import Enum
from typing import Optional


class ErrorCode(Enum):
    """Error codes for TogoMQ operations."""

    CONNECTION = "connection"
    AUTH = "auth"
    VALIDATION = "validation"
    PUBLISH = "publish"
    SUBSCRIBE = "subscribe"
    STREAM = "stream"
    CONFIGURATION = "configuration"


class TogoMQError(Exception):
    """Custom exception for TogoMQ SDK errors.

    Attributes:
        code: The error code indicating the type of error.
        message: A descriptive error message.
        details: Optional additional error details.
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Optional[str] = None,
    ) -> None:
        """Initialize a TogoMQ error.

        Args:
            code: The error code.
            message: The error message.
            details: Optional additional error details.
        """
        self.code = code
        self.message = message
        self.details = details
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the error message."""
        msg = f"[{self.code.value.upper()}] {self.message}"
        if self.details:
            msg += f"\nDetails: {self.details}"
        return msg

    def __str__(self) -> str:
        """String representation of the error."""
        return self._format_message()

    def __repr__(self) -> str:
        """Repr of the error."""
        return f"TogoMQError(code={self.code}, message={self.message!r})"
