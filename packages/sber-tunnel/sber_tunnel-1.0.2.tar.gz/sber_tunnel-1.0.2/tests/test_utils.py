"""Tests for utility functions."""
import pytest
import sys
from io import StringIO
from sber_tunnel.core.utils import safe_str, safe_print, get_safe_error_message


def test_safe_str_normal_string():
    """Test safe_str with normal string."""
    result = safe_str("Hello, World!")
    assert result == "Hello, World!"


def test_safe_str_unicode():
    """Test safe_str with unicode characters."""
    result = safe_str("Привет, мир!")
    assert "Привет" in result or result != '<unprintable object>'


def test_safe_str_exception():
    """Test safe_str with exception object."""
    exc = ValueError("Test error")
    result = safe_str(exc)
    assert "Test error" in result


def test_safe_print_normal():
    """Test safe_print with normal string."""
    output = StringIO()
    safe_print("Test message", file=output)
    assert output.getvalue() == "Test message\n"


def test_safe_print_unicode():
    """Test safe_print with unicode characters."""
    output = StringIO()
    safe_print("Тест 测试", file=output)
    result = output.getvalue()
    # Should not raise exception
    assert len(result) > 0


def test_get_safe_error_message():
    """Test get_safe_error_message with exception."""
    exc = ValueError("Test error message")
    result = get_safe_error_message(exc)
    assert "Test error message" in result


def test_get_safe_error_message_unicode():
    """Test get_safe_error_message with unicode in exception."""
    exc = ValueError("Ошибка соединения")
    result = get_safe_error_message(exc)
    # Should return something, even if encoding fails
    assert len(result) > 0
    assert "ValueError" in result or "Ошибка" in result


class CustomException(Exception):
    """Custom exception for testing."""
    def __str__(self):
        raise UnicodeEncodeError('latin-1', 'test', 0, 1, 'test')


def test_get_safe_error_message_encoding_error():
    """Test get_safe_error_message with exception that raises encoding error."""
    exc = CustomException("Test")
    result = get_safe_error_message(exc)
    # Should not raise exception
    assert "CustomException" in result or "encoding error" in result
