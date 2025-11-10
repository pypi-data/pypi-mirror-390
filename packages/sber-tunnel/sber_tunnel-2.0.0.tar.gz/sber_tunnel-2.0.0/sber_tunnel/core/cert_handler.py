"""Certificate handling utilities for p12 certificates."""
import tempfile
import os
from pathlib import Path
from typing import Optional, Tuple
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend


class CertificateHandler:
    """Handler for p12 certificate extraction."""

    def __init__(self):
        """Initialize certificate handler."""
        self.temp_cert_path: Optional[str] = None
        self.temp_key_path: Optional[str] = None
        self._temp_files = []

    def extract_p12(self, p12_path: str, password: Optional[str] = None) -> Tuple[str, str]:
        """Extract certificate and private key from p12 file.

        Args:
            p12_path: Path to p12 certificate file
            password: Password for p12 file (optional)

        Returns:
            Tuple of (cert_path, key_path) - paths to extracted PEM files

        Raises:
            ValueError: If p12 file cannot be read or parsed
        """
        try:
            # Read p12 file
            with open(p12_path, 'rb') as f:
                p12_data = f.read()

            # Parse p12 with password
            password_bytes = password.encode() if password else None

            try:
                private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
                    p12_data,
                    password_bytes,
                    backend=default_backend()
                )
            except Exception as e:
                raise ValueError(f"Failed to parse p12 certificate: {e}")

            if not private_key or not certificate:
                raise ValueError("p12 file does not contain required private key or certificate")

            # Create temporary files for cert and key
            cert_fd, cert_path = tempfile.mkstemp(suffix='.pem', prefix='sber_tunnel_cert_')
            key_fd, key_path = tempfile.mkstemp(suffix='.pem', prefix='sber_tunnel_key_')

            self._temp_files.extend([cert_path, key_path])

            # Write certificate to PEM file
            with os.fdopen(cert_fd, 'wb') as cert_file:
                cert_pem = certificate.public_bytes(
                    encoding=serialization.Encoding.PEM
                )
                cert_file.write(cert_pem)

                # Write additional certificates if present (certificate chain)
                if additional_certs:
                    for cert in additional_certs:
                        cert_pem = cert.public_bytes(
                            encoding=serialization.Encoding.PEM
                        )
                        cert_file.write(cert_pem)

            # Write private key to PEM file
            with os.fdopen(key_fd, 'wb') as key_file:
                key_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                )
                key_file.write(key_pem)

            # Set restrictive permissions on key file
            os.chmod(key_path, 0o600)

            self.temp_cert_path = cert_path
            self.temp_key_path = key_path

            return cert_path, key_path

        except FileNotFoundError:
            raise ValueError(f"p12 certificate file not found: {p12_path}")
        except Exception as e:
            self.cleanup()
            raise ValueError(f"Error processing p12 certificate: {e}")

    def cleanup(self):
        """Clean up temporary certificate files."""
        for temp_file in self._temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                print(f"Warning: Failed to delete temporary file {temp_file}: {e}")

        self._temp_files.clear()
        self.temp_cert_path = None
        self.temp_key_path = None

    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
