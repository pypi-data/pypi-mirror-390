"""Configuration for TogoMQ client."""

from typing import Optional

from togomq.errors import ErrorCode, TogoMQError
from togomq.logger import LogLevel


class Config:
    """Configuration for TogoMQ client.

    Attributes:
        host: TogoMQ server hostname (default: q.togomq.io).
        port: TogoMQ server port (default: 5123).
        token: Authentication token (required).
        log_level: Logging level (default: info).
        use_tls: Whether to use TLS encryption (default: True).
    """

    DEFAULT_HOST = "q.togomq.io"
    DEFAULT_PORT = 5123
    DEFAULT_LOG_LEVEL = LogLevel.INFO
    DEFAULT_USE_TLS = True

    def __init__(
        self,
        token: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        log_level: Optional[str] = None,
        use_tls: Optional[bool] = None,
    ) -> None:
        """Initialize TogoMQ configuration.

        Args:
            token: Authentication token (required).
            host: TogoMQ server hostname.
            port: TogoMQ server port.
            log_level: Logging level (debug, info, warn, error, none).
            use_tls: Whether to use TLS encryption.

        Raises:
            TogoMQError: If configuration is invalid.
        """
        if not token or not isinstance(token, str) or not token.strip():
            raise TogoMQError(
                code=ErrorCode.CONFIGURATION,
                message="Token is required and must be a non-empty string",
            )

        self.token = token.strip()
        self.host = host if host is not None else self.DEFAULT_HOST
        self.port = port if port is not None else self.DEFAULT_PORT
        self.log_level = log_level if log_level is not None else self.DEFAULT_LOG_LEVEL
        self.use_tls = use_tls if use_tls is not None else self.DEFAULT_USE_TLS

        self._validate()

    def _validate(self) -> None:
        """Validate configuration parameters.

        Raises:
            TogoMQError: If configuration is invalid.
        """
        if not isinstance(self.host, str) or not self.host.strip():
            raise TogoMQError(
                code=ErrorCode.CONFIGURATION,
                message="Host must be a non-empty string",
            )

        if not isinstance(self.port, int) or self.port <= 0 or self.port > 65535:
            raise TogoMQError(
                code=ErrorCode.CONFIGURATION,
                message="Port must be an integer between 1 and 65535",
            )

        valid_log_levels = {
            LogLevel.DEBUG,
            LogLevel.INFO,
            LogLevel.WARN,
            LogLevel.ERROR,
            LogLevel.NONE,
        }
        if self.log_level.lower() not in valid_log_levels:
            raise TogoMQError(
                code=ErrorCode.CONFIGURATION,
                message=f"Invalid log level. Must be one of: {', '.join(valid_log_levels)}",
            )

    def get_address(self) -> str:
        """Get the server address.

        Returns:
            The server address in format "host:port".
        """
        return f"{self.host}:{self.port}"

    def __repr__(self) -> str:
        """Repr of the config."""
        return (
            f"Config(host={self.host!r}, port={self.port}, "
            f"log_level={self.log_level!r}, use_tls={self.use_tls})"
        )
