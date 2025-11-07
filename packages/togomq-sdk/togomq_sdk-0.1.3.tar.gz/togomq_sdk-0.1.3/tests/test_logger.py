"""Unit tests for logger module."""

import logging

from togomq.logger import LogLevel, get_logger, setup_logger


class TestLogger:
    """Tests for logger module."""

    def test_setup_logger_default(self) -> None:
        """Test setup logger with default level."""
        logger = setup_logger("test.default")

        assert logger.name == "test.default"
        assert logger.level == logging.INFO
        assert not logger.propagate

    def test_setup_logger_debug(self) -> None:
        """Test setup logger with debug level."""
        logger = setup_logger("test.debug", LogLevel.DEBUG)

        assert logger.level == logging.DEBUG
        assert len(logger.handlers) > 0

    def test_setup_logger_info(self) -> None:
        """Test setup logger with info level."""
        logger = setup_logger("test.info", LogLevel.INFO)
        assert logger.level == logging.INFO

    def test_setup_logger_warn(self) -> None:
        """Test setup logger with warn level."""
        logger = setup_logger("test.warn", LogLevel.WARN)
        assert logger.level == logging.WARNING

    def test_setup_logger_error(self) -> None:
        """Test setup logger with error level."""
        logger = setup_logger("test.error", LogLevel.ERROR)
        assert logger.level == logging.ERROR

    def test_setup_logger_none(self) -> None:
        """Test setup logger with none level (disabled)."""
        logger = setup_logger("test.none", LogLevel.NONE)

        # Should have no handlers when disabled
        assert len(logger.handlers) == 0
        assert logger.level > logging.CRITICAL

    def test_get_logger(self) -> None:
        """Test get_logger function."""
        logger = get_logger("test.get")
        assert logger.name == "test.get"
        assert isinstance(logger, logging.Logger)

    def test_logger_case_insensitive(self) -> None:
        """Test that log level is case insensitive."""
        logger1 = setup_logger("test.case1", "DEBUG")
        logger2 = setup_logger("test.case2", "debug")
        logger3 = setup_logger("test.case3", "DeBuG")

        assert logger1.level == logging.DEBUG
        assert logger2.level == logging.DEBUG
        assert logger3.level == logging.DEBUG

    def test_logger_removes_existing_handlers(self) -> None:
        """Test that setup removes existing handlers."""
        logger_name = "test.handlers"

        # Setup first time
        logger1 = setup_logger(logger_name, LogLevel.INFO)
        initial_handlers = len(logger1.handlers)

        # Setup again
        logger2 = setup_logger(logger_name, LogLevel.DEBUG)

        # Should have same number of handlers (old ones removed)
        assert len(logger2.handlers) == initial_handlers
        assert logger1 is logger2  # Same logger object
