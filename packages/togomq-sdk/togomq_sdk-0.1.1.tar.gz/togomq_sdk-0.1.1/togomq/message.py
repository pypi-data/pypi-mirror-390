"""Message model for TogoMQ SDK."""

from typing import Optional


class Message:
    """Represents a message in TogoMQ.

    For publishing:
        topic: Message topic (required)
        body: Message payload
        variables: Custom key-value metadata
        postpone: Delay in seconds before message is available
        retention: How long to keep message (seconds)

    For receiving:
        topic: Message topic
        uuid: Unique message identifier
        body: Message payload
        variables: Custom key-value metadata
    """

    def __init__(
        self,
        topic: str,
        body: Optional[bytes] = None,
        variables: Optional[dict[str, str]] = None,
        postpone: Optional[int] = None,
        retention: Optional[int] = None,
        uuid: Optional[str] = None,
    ) -> None:
        """Initialize a message.

        Args:
            topic: Message topic (required).
            body: Message payload.
            variables: Custom key-value metadata.
            postpone: Delay in seconds before message is available.
            retention: How long to keep message (seconds).
            uuid: Unique message identifier (set by server on receive).
        """
        self.topic = topic
        self.body = body if body is not None else b""
        self.variables = variables if variables is not None else {}
        self.postpone = postpone if postpone is not None else 0
        self.retention = retention if retention is not None else 0
        self.uuid = uuid

    def with_variables(self, variables: dict[str, str]) -> "Message":
        """Set message variables (builder pattern).

        Args:
            variables: Custom key-value metadata.

        Returns:
            Self for chaining.
        """
        self.variables = variables
        return self

    def with_postpone(self, postpone: int) -> "Message":
        """Set postpone delay (builder pattern).

        Args:
            postpone: Delay in seconds before message is available.

        Returns:
            Self for chaining.
        """
        self.postpone = postpone
        return self

    def with_retention(self, retention: int) -> "Message":
        """Set retention period (builder pattern).

        Args:
            retention: How long to keep message (seconds).

        Returns:
            Self for chaining.
        """
        self.retention = retention
        return self

    def __repr__(self) -> str:
        """Repr of the message."""
        return (
            f"Message(topic={self.topic!r}, body_len={len(self.body)}, "
            f"variables={self.variables}, postpone={self.postpone}, "
            f"retention={self.retention}, uuid={self.uuid!r})"
        )

    def __str__(self) -> str:
        """String representation of the message."""
        body_preview = self.body[:50] if len(self.body) > 50 else self.body
        return f"Message(topic={self.topic!r}, body={body_preview!r}...)"
