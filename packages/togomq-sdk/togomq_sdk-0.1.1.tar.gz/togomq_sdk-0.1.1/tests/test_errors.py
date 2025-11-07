"""Unit tests for errors module."""

import pytest

from togomq.errors import ErrorCode, TogoMQError


class TestErrorCode:
    """Tests for ErrorCode enum."""

    def test_error_code_values(self) -> None:
        """Test that error codes have correct values."""
        assert ErrorCode.CONNECTION.value == "connection"
        assert ErrorCode.AUTH.value == "auth"
        assert ErrorCode.VALIDATION.value == "validation"
        assert ErrorCode.PUBLISH.value == "publish"
        assert ErrorCode.SUBSCRIBE.value == "subscribe"
        assert ErrorCode.STREAM.value == "stream"
        assert ErrorCode.CONFIGURATION.value == "configuration"


class TestTogoMQError:
    """Tests for TogoMQError exception."""

    def test_error_basic(self) -> None:
        """Test basic error creation."""
        error = TogoMQError(code=ErrorCode.CONNECTION, message="Connection failed")

        assert error.code == ErrorCode.CONNECTION
        assert error.message == "Connection failed"
        assert error.details is None

    def test_error_with_details(self) -> None:
        """Test error with details."""
        error = TogoMQError(
            code=ErrorCode.AUTH,
            message="Authentication failed",
            details="Invalid token format",
        )

        assert error.code == ErrorCode.AUTH
        assert error.message == "Authentication failed"
        assert error.details == "Invalid token format"

    def test_error_str(self) -> None:
        """Test error string representation."""
        error = TogoMQError(code=ErrorCode.VALIDATION, message="Invalid input")
        error_str = str(error)

        assert "VALIDATION" in error_str
        assert "Invalid input" in error_str

    def test_error_str_with_details(self) -> None:
        """Test error string with details."""
        error = TogoMQError(
            code=ErrorCode.PUBLISH,
            message="Publish failed",
            details="Network timeout",
        )
        error_str = str(error)

        assert "PUBLISH" in error_str
        assert "Publish failed" in error_str
        assert "Network timeout" in error_str
        assert "Details:" in error_str

    def test_error_repr(self) -> None:
        """Test error repr."""
        error = TogoMQError(code=ErrorCode.STREAM, message="Stream error")
        repr_str = repr(error)

        assert "TogoMQError" in repr_str
        assert "ErrorCode.STREAM" in repr_str
        assert "Stream error" in repr_str

    def test_error_is_exception(self) -> None:
        """Test that TogoMQError is an Exception."""
        error = TogoMQError(code=ErrorCode.CONNECTION, message="Test")
        assert isinstance(error, Exception)

    def test_error_can_be_raised(self) -> None:
        """Test that error can be raised and caught."""
        with pytest.raises(TogoMQError) as exc_info:
            raise TogoMQError(code=ErrorCode.CONNECTION, message="Test error")

        assert exc_info.value.code == ErrorCode.CONNECTION
        assert exc_info.value.message == "Test error"

    def test_error_code_comparison(self) -> None:
        """Test comparing error codes."""
        error1 = TogoMQError(code=ErrorCode.AUTH, message="Auth error")
        error2 = TogoMQError(code=ErrorCode.AUTH, message="Different message")
        error3 = TogoMQError(code=ErrorCode.VALIDATION, message="Validation error")

        assert error1.code == error2.code
        assert error1.code != error3.code
