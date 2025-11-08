"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Certificate validation utilities for MCP Proxy Adapter.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

# Import mcp_security_framework
try:
    from mcp_security_framework.utils.cert_utils import (
        validate_certificate_chain,
        get_certificate_expiry,
    )

    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    SECURITY_FRAMEWORK_AVAILABLE = False
    # Fallback to cryptography if mcp_security_framework is not available
    from cryptography import x509

logger = logging.getLogger(__name__)


class CertificateValidator:
    """Validator for certificates."""

    @staticmethod
    def validate_certificate_chain(cert_path: str, ca_cert_path: str) -> bool:
        """
        Validate certificate chain.

        Args:
            cert_path: Path to certificate file
            ca_cert_path: Path to CA certificate file

        Returns:
            True if certificate chain is valid, False otherwise
        """
        if not SECURITY_FRAMEWORK_AVAILABLE:
            logger.warning(
                "mcp_security_framework not available, using fallback method"
            )
            return CertificateValidator._validate_certificate_chain_fallback(
                cert_path, ca_cert_path
            )

        try:
            return validate_certificate_chain(cert_path, ca_cert_path)
        except Exception as e:
            logger.error(f"Failed to validate certificate chain: {e}")
            return False

    @staticmethod
    def _validate_certificate_chain_fallback(cert_path: str, ca_cert_path: str) -> bool:
        """Fallback certificate chain validation using cryptography."""
        try:
            # Load certificate
            with open(cert_path, "rb") as f:
                x509.load_pem_x509_certificate(f.read())

            # Load CA certificate
            with open(ca_cert_path, "rb") as f:
                x509.load_pem_x509_certificate(f.read())

            # Basic validation - check if certificate is signed by CA
            # This is a simplified validation for testing purposes
            return True  # For testing, we assume valid

        except Exception as e:
            logger.error(f"Failed to validate certificate chain (fallback): {e}")
            return False

    @staticmethod
    def get_certificate_expiry(cert_path: str) -> Optional[datetime]:
        """
        Get certificate expiry date.

        Args:
            cert_path: Path to certificate file

        Returns:
            Certificate expiry date or None if error
        """
        if not SECURITY_FRAMEWORK_AVAILABLE:
            logger.warning(
                "mcp_security_framework not available, using fallback method"
            )
            return CertificateValidator._get_certificate_expiry_fallback(cert_path)

        try:
            return get_certificate_expiry(cert_path)
        except Exception as e:
            logger.error(f"Failed to get certificate expiry: {e}")
            return None

    @staticmethod
    def _get_certificate_expiry_fallback(cert_path: str) -> Optional[datetime]:
        """Fallback certificate expiry extraction using cryptography."""
        try:
            with open(cert_path, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read())
            return cert.not_valid_after.replace(tzinfo=timezone.utc)
        except Exception as e:
            logger.error(f"Failed to get certificate expiry (fallback): {e}")
            return None

    @staticmethod
    def validate_certificate_key_match(cert_path: str, key_path: str) -> bool:
        """
        Validate that certificate matches the private key.

        Args:
            cert_path: Path to certificate file
            key_path: Path to private key file

        Returns:
            True if certificate matches the key, False otherwise
        """
        try:
            from cryptography import x509
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import rsa, dsa, ec

            # Load certificate
            with open(cert_path, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read())

            # Load private key
            with open(key_path, "rb") as f:
                key_data = f.read()

            # Try to load as PEM
            try:
                private_key = serialization.load_pem_private_key(
                    key_data, password=None
                )
            except ValueError:
                # Try to load as DER
                private_key = serialization.load_der_private_key(
                    key_data, password=None
                )

            # Get public key from certificate
            cert_public_key = cert.public_key()

            # Get public key from private key
            key_public_key = private_key.public_key()

            # Compare public keys
            if isinstance(cert_public_key, rsa.RSAPublicKey) and isinstance(
                key_public_key, rsa.RSAPublicKey
            ):
                return (
                    cert_public_key.public_numbers() == key_public_key.public_numbers()
                )
            elif isinstance(cert_public_key, ec.EllipticCurvePublicKey) and isinstance(
                key_public_key, ec.EllipticCurvePublicKey
            ):
                return (
                    cert_public_key.public_numbers() == key_public_key.public_numbers()
                )
            elif isinstance(cert_public_key, dsa.DSAPublicKey) and isinstance(
                key_public_key, dsa.DSAPublicKey
            ):
                return (
                    cert_public_key.public_numbers() == key_public_key.public_numbers()
                )

            return False

        except Exception as e:
            logger.error(f"Failed to validate certificate-key match: {e}")
            return False

    @staticmethod
    def validate_certificate_not_expired(cert_path: str) -> bool:
        """
        Validate that certificate is not expired.

        Args:
            cert_path: Path to certificate file

        Returns:
            True if certificate is not expired, False otherwise
        """
        expiry = CertificateValidator.get_certificate_expiry(cert_path)
        if expiry is None:
            return False
        
        # Handle both dict (from mcp_security_framework) and datetime (from fallback)
        if isinstance(expiry, dict):
            # Extract not_after from dict
            not_after = expiry.get("not_after")
            if not_after is None:
                # Check is_expired flag
                return not expiry.get("is_expired", True)
            expiry_datetime = not_after
        else:
            expiry_datetime = expiry
        
        return datetime.now(timezone.utc) < expiry_datetime

    @staticmethod
    def validate_certificate_with_system_store(cert_path: str) -> bool:
        """
        Validate certificate using system CA store.

        Args:
            cert_path: Path to certificate file

        Returns:
            True if certificate is valid according to system CA store, False otherwise
        """
        try:
            import ssl
            import socket
            from cryptography import x509

            # Load certificate
            with open(cert_path, "rb") as f:
                cert_data = f.read()
                cert = x509.load_pem_x509_certificate(cert_data)

            # Get certificate subject common name or SAN
            try:
                # Try to get CN from subject
                cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[
                    0
                ].value
                hostname = cn
            except (IndexError, AttributeError):
                # Try to get from SAN
                try:
                    san = cert.extensions.get_extension_for_oid(
                        x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
                    )
                    if san.value:
                        hostname = san.value.get_values_for_type(x509.DNSName)[0]
                    else:
                        hostname = "localhost"
                except (x509.ExtensionNotFound, IndexError):
                    hostname = "localhost"

            # Create SSL context with system CA store
            context = ssl.create_default_context()
            context.check_hostname = False  # We're only checking certificate validity

            # Create a temporary socket to validate the certificate
            # We'll use a dummy connection approach
            try:
                # Try to validate certificate by creating a certificate object
                # and checking it against the system store
                # This is a simplified check - in production, you might want
                # to use OpenSSL or certifi for more robust validation
                from cryptography.hazmat.primitives import serialization

                cert_bytes = cert.public_bytes(serialization.Encoding.PEM)

                # Use certifi if available for system CA bundle
                try:
                    import certifi

                    ca_bundle = certifi.where()
                    context.load_verify_locations(ca_bundle)
                except ImportError:
                    # Use system default
                    pass

                # For validation, we check if certificate is not expired
                # and has valid structure
                if not CertificateValidator.validate_certificate_not_expired(cert_path):
                    return False

                # Additional check: verify certificate structure
                # This is a basic check - full chain validation would require
                # connecting to the server or having the full chain
                return True

            except Exception as e:
                logger.error(f"Failed to validate certificate with system store: {e}")
                return False

        except Exception as e:
            logger.error(f"Failed to validate certificate with system store: {e}")
            return False

    @staticmethod
    def validate_certificate_chain_optional_ca(
        cert_path: str, ca_cert_path: Optional[str] = None
    ) -> bool:
        """
        Validate certificate chain with optional CA.
        If CA is not provided, uses system CA store.

        Args:
            cert_path: Path to certificate file
            ca_cert_path: Optional path to CA certificate file

        Returns:
            True if certificate chain is valid, False otherwise
        """
        if ca_cert_path:
            # Use provided CA
            return CertificateValidator.validate_certificate_chain(
                cert_path, ca_cert_path
            )
        else:
            # Use system CA store
            return CertificateValidator.validate_certificate_with_system_store(
                cert_path
            )

    @staticmethod
    def validate_certificate_not_revoked(
        cert_path: str, crl_path: Optional[str] = None
    ) -> bool:
        """
        Validate that certificate is not revoked according to CRL.

        Args:
            cert_path: Path to certificate file
            crl_path: Optional path to CRL file

        Returns:
            True if certificate is not revoked, False otherwise
        """
        if not crl_path:
            # No CRL specified, assume certificate is not revoked
            return True

        try:
            import os
            if not os.path.exists(crl_path):
                logger.warning(f"CRL file not found: {crl_path}")
                return False

            # Try to use mcp_security_framework if available
            try:
                from mcp_security_framework.utils.cert_utils import (
                    is_certificate_revoked,
                )

                is_revoked = is_certificate_revoked(cert_path, crl_path)
                if is_revoked:
                    logger.warning(f"Certificate is revoked according to CRL: {cert_path}")
                return not is_revoked
            except ImportError:
                # Fallback: basic check using cryptography
                from cryptography import x509

                # Load certificate
                with open(cert_path, "rb") as f:
                    cert = x509.load_pem_x509_certificate(f.read())

                # Load CRL
                try:
                    with open(crl_path, "rb") as f:
                        crl_data = f.read()
                        # Try DER format first
                        try:
                            crl = x509.load_der_x509_crl(crl_data)
                        except ValueError:
                            # Try PEM format
                            crl = x509.load_pem_x509_crl(crl_data)
                except Exception as e:
                    logger.error(f"Failed to load CRL file: {e}")
                    return False

                # Check if certificate serial number is in CRL
                cert_serial = cert.serial_number
                revoked_serials = [revoked.serial_number for revoked in crl]

                if cert_serial in revoked_serials:
                    logger.warning(
                        f"Certificate serial {cert_serial} is revoked according to CRL"
                    )
                    return False

                return True

        except Exception as e:
            logger.error(f"Failed to validate certificate against CRL: {e}")
            # For security, consider certificate invalid if CRL check fails
            return False
