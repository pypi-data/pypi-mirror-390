"""Utility functions for sber-tunnel."""
import sys
from typing import Any


def safe_str(obj: Any) -> str:
    """Safely convert object to string, handling encoding issues.

    Args:
        obj: Object to convert to string

    Returns:
        String representation of object
    """
    try:
        return str(obj)
    except UnicodeEncodeError:
        # If str() fails due to encoding, try repr()
        try:
            return repr(obj)
        except:
            # Last resort: convert to bytes and decode with error handling
            return str(obj).encode('utf-8', errors='replace').decode('utf-8')
    except Exception:
        # Absolute fallback
        return '<unprintable object>'


def safe_print(message: str, file=None):
    """Safely print message, handling encoding issues.

    Args:
        message: Message to print
        file: File object to write to (default: sys.stdout)
    """
    if file is None:
        file = sys.stdout

    try:
        print(message, file=file)
    except UnicodeEncodeError:
        # Try encoding to UTF-8 with replacement
        try:
            safe_message = message.encode('utf-8', errors='replace').decode('utf-8')
            print(safe_message, file=file)
        except:
            # Last resort: print ASCII-only version
            ascii_message = message.encode('ascii', errors='replace').decode('ascii')
            print(ascii_message, file=file)


def get_safe_error_message(exception: Exception) -> str:
    """Get error message from exception, handling encoding issues.

    Args:
        exception: Exception object

    Returns:
        Safe error message string
    """
    try:
        # Try to get the exception message
        message = str(exception)
        # Verify it can be encoded
        message.encode('utf-8')
        return message
    except:
        # If that fails, try repr
        try:
            return repr(exception)
        except:
            # Last resort
            return f"{type(exception).__name__}: <encoding error>"
