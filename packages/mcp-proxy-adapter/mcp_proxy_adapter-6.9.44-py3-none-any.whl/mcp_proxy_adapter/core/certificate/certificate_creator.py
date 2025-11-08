"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Certificate creation utilities for MCP Proxy Adapter.
"""

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Import mcp_security_framework
try:
    from mcp_security_framework.core.cert_manager import (
        CertificateManager,
        CertificateConfig,
        CAConfig,
        ClientCertConfig,
        ServerCertConfig,
    )
    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    SECURITY_FRAMEWORK_AVAILABLE = False
    # Fallback to cryptography if mcp_security_framework is not available
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

logger = logging.getLogger(__name__)


class CertificateCreator:
    """Creator for various types of certificates."""

    # Default certificate validity period (1 year)
    DEFAULT_VALIDITY_DAYS = 365

    # Default key size
    DEFAULT_KEY_SIZE = 2048

    @staticmethod
    def create_ca_certificate(
        common_name: str,
        output_dir: str,
        validity_days: int = DEFAULT_VALIDITY_DAYS,
        key_size: int = DEFAULT_KEY_SIZE,
    ) -> Dict[str, str]:
        """
        Create a CA certificate and private key using mcp_security_framework.

        Args:
            common_name: Common name for the CA certificate
            output_dir: Directory to save certificate and key files
            validity_days: Certificate validity period in days
            key_size: RSA key size in bits

        Returns:
            Dictionary with paths to created files

        Raises:
            ValueError: If parameters are invalid
            OSError: If files cannot be created
        """
        if not SECURITY_FRAMEWORK_AVAILABLE:
            logger.warning("mcp_security_framework not available, using fallback method")
            return CertificateCreator._create_ca_certificate_fallback(
                common_name, output_dir, validity_days, key_size
            )

        try:
            # Validate parameters
            if not common_name or not common_name.strip():
                raise ValueError("Common name cannot be empty")

            if validity_days <= 0:
                raise ValueError("Validity days must be positive")

            if key_size < 1024:
                raise ValueError("Key size must be at least 1024 bits")

            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Configure CA using mcp_security_framework
            ca_config = CAConfig(
                common_name=common_name,
                organization="MCP Proxy Adapter CA",
                organizational_unit="Certificate Authority",
                country="US",
                state="Default State",
                locality="Default City",
                validity_days=validity_days,
                key_size=key_size,
                key_type="RSA",
            )

            # Create certificate manager
            cert_config = CertificateConfig(
                output_dir=output_dir,
                ca_cert_path=str(Path(output_dir) / f"{common_name}.crt"),
                ca_key_path=str(Path(output_dir) / f"{common_name}.key"),
            )

            cert_manager = CertificateManager(cert_config)

            # Generate CA certificate
            ca_pair = cert_manager.create_ca_certificate(ca_config)

            return {
                "cert_path": str(ca_pair.cert_path),
                "key_path": str(ca_pair.key_path),
            }

        except Exception as e:
            logger.error(f"Failed to create CA certificate: {e}")
            raise

    @staticmethod
    def _create_ca_certificate_fallback(
        common_name: str, output_dir: str, validity_days: int, key_size: int
    ) -> Dict[str, str]:
        """Fallback CA certificate creation using cryptography."""
        try:
            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
            )

            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Default State"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Default City"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MCP Proxy Adapter CA"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Certificate Authority"),
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            ])

            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.now(timezone.utc)
            ).not_valid_after(
                datetime.now(timezone.utc) + timedelta(days=validity_days)
            ).add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            ).add_extension(
                x509.KeyUsage(
                    key_cert_sign=True,
                    crl_sign=True,
                    digital_signature=True,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                    content_commitment=False,
                ),
                critical=True,
            ).sign(private_key, hashes.SHA256())

            # Save certificate and key
            cert_path = Path(output_dir) / f"{common_name}.crt"
            key_path = Path(output_dir) / f"{common_name}.key"

            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))

            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))

            return {
                "cert_path": str(cert_path),
                "key_path": str(key_path),
            }

        except Exception as e:
            logger.error(f"Failed to create CA certificate (fallback): {e}")
            raise

    @staticmethod
    def create_server_certificate(
        common_name: str,
        output_dir: str,
        ca_cert_path: str,
        ca_key_path: str,
        validity_days: int = DEFAULT_VALIDITY_DAYS,
        key_size: int = DEFAULT_KEY_SIZE,
        san_dns: Optional[List[str]] = None,
        san_ip: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """
        Create a server certificate signed by CA.

        Args:
            common_name: Common name for the server certificate
            output_dir: Directory to save certificate and key files
            ca_cert_path: Path to CA certificate
            ca_key_path: Path to CA private key
            validity_days: Certificate validity period in days
            key_size: RSA key size in bits
            san_dns: List of DNS names for SAN extension
            san_ip: List of IP addresses for SAN extension

        Returns:
            Dictionary with paths to created files
        """
        if not SECURITY_FRAMEWORK_AVAILABLE:
            logger.warning("mcp_security_framework not available, using fallback method")
            return CertificateCreator._create_server_certificate_fallback(
                common_name, output_dir, ca_cert_path, ca_key_path,
                validity_days, key_size, san_dns, san_ip
            )

        try:
            # Validate parameters
            if not common_name or not common_name.strip():
                raise ValueError("Common name cannot be empty")

            if not Path(ca_cert_path).exists():
                raise FileNotFoundError(f"CA certificate not found: {ca_cert_path}")

            if not Path(ca_key_path).exists():
                raise FileNotFoundError(f"CA key not found: {ca_key_path}")

            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Configure server certificate using mcp_security_framework
            server_config = ServerCertConfig(
                common_name=common_name,
                organization="MCP Proxy Adapter",
                organizational_unit="Server",
                country="US",
                state="Default State",
                locality="Default City",
                validity_days=validity_days,
                key_size=key_size,
                key_type="RSA",
                san_dns=san_dns or [],
                san_ip=san_ip or [],
            )

            # Create certificate manager
            cert_config = CertificateConfig(
                output_dir=output_dir,
                ca_cert_path=ca_cert_path,
                ca_key_path=ca_key_path,
            )

            cert_manager = CertificateManager(cert_config)

            # Generate server certificate
            server_pair = cert_manager.create_server_certificate(server_config)

            return {
                "cert_path": str(server_pair.cert_path),
                "key_path": str(server_pair.key_path),
            }

        except Exception as e:
            logger.error(f"Failed to create server certificate: {e}")
            raise

    @staticmethod
    def _create_server_certificate_fallback(
        common_name: str,
        output_dir: str,
        ca_cert_path: str,
        ca_key_path: str,
        validity_days: int,
        key_size: int,
        san_dns: Optional[List[str]],
        san_ip: Optional[List[str]],
    ) -> Dict[str, str]:
        """Fallback server certificate creation using cryptography."""
        try:
            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Load CA certificate and key
            with open(ca_cert_path, "rb") as f:
                ca_cert = x509.load_pem_x509_certificate(f.read())

            with open(ca_key_path, "rb") as f:
                ca_key = serialization.load_pem_private_key(f.read(), password=None)

            # Generate server private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
            )

            # Create certificate
            subject = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Default State"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Default City"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MCP Proxy Adapter"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Server"),
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            ])

            # Build certificate
            cert_builder = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                ca_cert.subject
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.now(timezone.utc)
            ).not_valid_after(
                datetime.now(timezone.utc) + timedelta(days=validity_days)
            )

            # Add SAN extension if provided
            if san_dns or san_ip:
                san_list = []
                if san_dns:
                    san_list.extend([x509.DNSName(name) for name in san_dns])
                if san_ip:
                    san_list.extend([x509.IPAddress(ip) for ip in san_ip])
                
                cert_builder = cert_builder.add_extension(
                    x509.SubjectAlternativeName(san_list),
                    critical=False,
                )

            cert = cert_builder.sign(ca_key, hashes.SHA256())

            # Save certificate and key
            cert_path = Path(output_dir) / f"{common_name}_server.crt"
            key_path = Path(output_dir) / f"{common_name}_server.key"

            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))

            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))

            return {
                "cert_path": str(cert_path),
                "key_path": str(key_path),
            }

        except Exception as e:
            logger.error(f"Failed to create server certificate (fallback): {e}")
            raise
