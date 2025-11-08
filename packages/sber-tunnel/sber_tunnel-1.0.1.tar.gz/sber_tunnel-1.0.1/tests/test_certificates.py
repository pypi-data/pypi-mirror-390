"""Tests for certificate handling."""
import pytest
import tempfile
import os
from pathlib import Path
from sber_tunnel.core.cert_handler import CertificateHandler


def test_certificate_handler_cleanup():
    """Test certificate handler cleanup."""
    handler = CertificateHandler()

    # Add some fake temp files
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_path = f.name
        handler._temp_files.append(temp_path)

    # Cleanup should remove the file
    handler.cleanup()
    assert not os.path.exists(temp_path)
    assert len(handler._temp_files) == 0


def test_certificate_handler_context_manager():
    """Test certificate handler as context manager."""
    temp_path = None

    with CertificateHandler() as handler:
        # Create a temp file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
            handler._temp_files.append(temp_path)

        assert os.path.exists(temp_path)

    # File should be cleaned up after context exit
    assert not os.path.exists(temp_path)


def test_extract_p12_invalid_file():
    """Test p12 extraction with invalid file."""
    handler = CertificateHandler()

    with pytest.raises(ValueError, match="p12 certificate file not found"):
        handler.extract_p12("/nonexistent/file.p12")


def test_extract_p12_invalid_format():
    """Test p12 extraction with invalid format."""
    handler = CertificateHandler()

    # Create a temp file with invalid content
    with tempfile.NamedTemporaryFile(delete=False, suffix='.p12') as f:
        f.write(b"invalid p12 content")
        temp_p12 = f.name

    try:
        with pytest.raises(ValueError, match="Failed to parse p12 certificate"):
            handler.extract_p12(temp_p12, "password")
    finally:
        os.unlink(temp_p12)


# Note: Testing with real p12 certificates requires having test certificates
# In production, you would generate test certificates for these tests
