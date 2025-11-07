"""Unit tests for configuration module."""

import pytest

from togomq.config import Config
from togomq.errors import ErrorCode, TogoMQError
from togomq.logger import LogLevel


class TestConfig:
    """Tests for Config class."""

    def test_config_with_defaults(self) -> None:
        """Test config creation with default values."""
        config = Config(token="test-token")

        assert config.token == "test-token"
        assert config.host == Config.DEFAULT_HOST
        assert config.port == Config.DEFAULT_PORT
        assert config.log_level == Config.DEFAULT_LOG_LEVEL
        assert config.use_tls == Config.DEFAULT_USE_TLS

    def test_config_with_custom_values(self) -> None:
        """Test config creation with custom values."""
        config = Config(
            token="test-token",
            host="custom.host.com",
            port=9999,
            log_level=LogLevel.DEBUG,
            use_tls=False,
        )

        assert config.token == "test-token"
        assert config.host == "custom.host.com"
        assert config.port == 9999
        assert config.log_level == LogLevel.DEBUG
        assert config.use_tls is False

    def test_config_empty_token(self) -> None:
        """Test that empty token raises error."""
        with pytest.raises(TogoMQError) as exc_info:
            Config(token="")

        assert exc_info.value.code == ErrorCode.CONFIGURATION
        assert "Token is required" in str(exc_info.value)

    def test_config_whitespace_token(self) -> None:
        """Test that whitespace-only token raises error."""
        with pytest.raises(TogoMQError) as exc_info:
            Config(token="   ")

        assert exc_info.value.code == ErrorCode.CONFIGURATION

    def test_config_token_stripped(self) -> None:
        """Test that token is stripped of whitespace."""
        config = Config(token="  test-token  ")
        assert config.token == "test-token"

    def test_config_invalid_host(self) -> None:
        """Test that invalid host raises error."""
        with pytest.raises(TogoMQError) as exc_info:
            Config(token="test-token", host="")

        assert exc_info.value.code == ErrorCode.CONFIGURATION
        assert "Host must be" in str(exc_info.value)

    def test_config_invalid_port_zero(self) -> None:
        """Test that port 0 raises error."""
        with pytest.raises(TogoMQError) as exc_info:
            Config(token="test-token", port=0)

        assert exc_info.value.code == ErrorCode.CONFIGURATION
        assert "Port must be" in str(exc_info.value)

    def test_config_invalid_port_negative(self) -> None:
        """Test that negative port raises error."""
        with pytest.raises(TogoMQError) as exc_info:
            Config(token="test-token", port=-1)

        assert exc_info.value.code == ErrorCode.CONFIGURATION

    def test_config_invalid_port_too_large(self) -> None:
        """Test that port > 65535 raises error."""
        with pytest.raises(TogoMQError) as exc_info:
            Config(token="test-token", port=65536)

        assert exc_info.value.code == ErrorCode.CONFIGURATION

    def test_config_invalid_log_level(self) -> None:
        """Test that invalid log level raises error."""
        with pytest.raises(TogoMQError) as exc_info:
            Config(token="test-token", log_level="invalid")

        assert exc_info.value.code == ErrorCode.CONFIGURATION
        assert "Invalid log level" in str(exc_info.value)

    def test_config_get_address(self) -> None:
        """Test get_address method."""
        config = Config(token="test-token", host="test.host.com", port=1234)
        assert config.get_address() == "test.host.com:1234"

    def test_config_repr(self) -> None:
        """Test string representation."""
        config = Config(token="test-token")
        repr_str = repr(config)

        assert "Config" in repr_str
        assert "q.togomq.io" in repr_str
        assert "5123" in repr_str
        assert "info" in repr_str
