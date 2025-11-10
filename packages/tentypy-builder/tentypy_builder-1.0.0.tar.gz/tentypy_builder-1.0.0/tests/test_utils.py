"""
Tests for TentyPy Utils
"""

import logging

from tentypy.utils.logger import setup_logger


class TestLogger:
    """Tests for logger utilities"""

    def test_setup_logger_default(self):
        """Test logger setup with defaults"""
        logger = setup_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0

    def test_setup_logger_custom_level(self):
        """Test logger with custom level"""
        logger = setup_logger("test_debug", level=logging.DEBUG)
        assert logger.level == logging.DEBUG

    def test_setup_logger_custom_format(self):
        """Test logger with custom format"""
        custom_format = "%(name)s - %(message)s"
        logger = setup_logger("test_format", format_string=custom_format)
        assert len(logger.handlers) > 0

    def test_logger_no_duplicate_handlers(self):
        """Test that logger doesn't create duplicate handlers"""
        logger1 = setup_logger("test_duplicate")
        handler_count1 = len(logger1.handlers)

        logger2 = setup_logger("test_duplicate")
        handler_count2 = len(logger2.handlers)

        assert handler_count1 == handler_count2
