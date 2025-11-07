"""Subscribe options for TogoMQ client."""

from typing import Optional


class SubscribeOptions:
    """Options for subscribing to messages.

    Attributes:
        topic: Topic to subscribe to (required). Use "*" for all topics,
            or wildcards like "orders.*".
        batch: Maximum number of messages to receive at once
            (default: 0 = server default 1000).
        speed_per_sec: Rate limit for message delivery per second
            (default: 0 = unlimited).
    """

    def __init__(
        self,
        topic: str,
        batch: Optional[int] = None,
        speed_per_sec: Optional[int] = None,
    ) -> None:
        """Initialize subscribe options.

        Args:
            topic: Topic to subscribe to (required).
            batch: Maximum number of messages to receive at once.
            speed_per_sec: Rate limit for message delivery per second.
        """
        self.topic = topic
        self.batch = batch if batch is not None else 0
        self.speed_per_sec = speed_per_sec if speed_per_sec is not None else 0

    def with_batch(self, batch: int) -> "SubscribeOptions":
        """Set batch size (builder pattern).

        Args:
            batch: Maximum number of messages to receive at once.

        Returns:
            Self for chaining.
        """
        self.batch = batch
        return self

    def with_speed_per_sec(self, speed_per_sec: int) -> "SubscribeOptions":
        """Set rate limit (builder pattern).

        Args:
            speed_per_sec: Rate limit for message delivery per second.

        Returns:
            Self for chaining.
        """
        self.speed_per_sec = speed_per_sec
        return self

    def __repr__(self) -> str:
        """Repr of the subscribe options."""
        return (
            f"SubscribeOptions(topic={self.topic!r}, batch={self.batch}, "
            f"speed_per_sec={self.speed_per_sec})"
        )
