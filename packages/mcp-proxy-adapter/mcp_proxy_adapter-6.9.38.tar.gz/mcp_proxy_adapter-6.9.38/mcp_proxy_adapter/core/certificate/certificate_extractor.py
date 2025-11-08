"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Certificate information extraction utilities for MCP Proxy Adapter.
"""

import logging
from typing import List

# Import mcp_security_framework
try:
    from mcp_security_framework.utils.cert_utils import (
        parse_certificate,
        extract_roles_from_certificate,
        extract_permissions_from_certificate,
    )
    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    SECURITY_FRAMEWORK_AVAILABLE = False
    # Fallback to cryptography if mcp_security_framework is not available
    from cryptography import x509

logger = logging.getLogger(__name__)


class CertificateExtractor:
    """Extractor for certificate information."""

    # Custom OID for roles (same as in RoleUtils)
    ROLE_EXTENSION_OID = "1.3.6.1.4.1.99999.1"

    @staticmethod
    def extract_roles_from_certificate(cert_path: str) -> List[str]:
        """
        Extract roles from certificate.

        Args:
            cert_path: Path to certificate file

        Returns:
            List of roles found in certificate
        """
        if not SECURITY_FRAMEWORK_AVAILABLE:
            logger.warning("mcp_security_framework not available, using fallback method")
            return CertificateExtractor._extract_roles_from_certificate_fallback(cert_path)

        try:
            return extract_roles_from_certificate(cert_path)
        except Exception as e:
            logger.error(f"Failed to extract roles from certificate: {e}")
            return []

    @staticmethod
    def _extract_roles_from_certificate_fallback(cert_path: str) -> List[str]:
        """Fallback role extraction using cryptography."""
        try:
            with open(cert_path, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read())

            # Look for custom role extension
            try:
                role_extension = cert.extensions.get_extension_for_oid(
                    x509.ObjectIdentifier(CertificateExtractor.ROLE_EXTENSION_OID)
                )
                if role_extension:
                    # Parse roles from extension value
                    roles_str = role_extension.value.value.decode('utf-8')
                    return [role.strip() for role in roles_str.split(',') if role.strip()]
            except x509.ExtensionNotFound:
                pass

            # Fallback: look for roles in subject alternative name
            try:
                san_extension = cert.extensions.get_extension_for_oid(
                    x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
                )
                if san_extension:
                    roles = []
                    for name in san_extension.value:
                        if isinstance(name, x509.DNSName):
                            # Check if this looks like a role (e.g., role:admin)
                            if name.value.startswith('role:'):
                                roles.append(name.value[5:])  # Remove 'role:' prefix
                    return roles
            except x509.ExtensionNotFound:
                pass

            return []

        except Exception as e:
            logger.error(f"Failed to extract roles from certificate (fallback): {e}")
            return []

    @staticmethod
    def extract_roles_from_certificate_object(cert) -> List[str]:
        """
        Extract roles from certificate object.

        Args:
            cert: Certificate object

        Returns:
            List of roles found in certificate
        """
        try:
            # Look for custom role extension
            try:
                role_extension = cert.extensions.get_extension_for_oid(
                    x509.ObjectIdentifier(CertificateExtractor.ROLE_EXTENSION_OID)
                )
                if role_extension:
                    # Parse roles from extension value
                    roles_str = role_extension.value.value.decode('utf-8')
                    return [role.strip() for role in roles_str.split(',') if role.strip()]
            except x509.ExtensionNotFound:
                pass

            # Fallback: look for roles in subject alternative name
            try:
                san_extension = cert.extensions.get_extension_for_oid(
                    x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
                )
                if san_extension:
                    roles = []
                    for name in san_extension.value:
                        if isinstance(name, x509.DNSName):
                            # Check if this looks like a role (e.g., role:admin)
                            if name.value.startswith('role:'):
                                roles.append(name.value[5:])  # Remove 'role:' prefix
                    return roles
            except x509.ExtensionNotFound:
                pass

            return []

        except Exception as e:
            logger.error(f"Failed to extract roles from certificate object: {e}")
            return []

    @staticmethod
    def extract_permissions_from_certificate(cert_path: str) -> List[str]:
        """
        Extract permissions from certificate.

        Args:
            cert_path: Path to certificate file

        Returns:
            List of permissions found in certificate
        """
        if not SECURITY_FRAMEWORK_AVAILABLE:
            logger.warning("mcp_security_framework not available, using fallback method")
            return CertificateExtractor._extract_permissions_from_certificate_fallback(cert_path)

        try:
            return extract_permissions_from_certificate(cert_path)
        except Exception as e:
            logger.error(f"Failed to extract permissions from certificate: {e}")
            return []

    @staticmethod
    def _extract_permissions_from_certificate_fallback(cert_path: str) -> List[str]:
        """Fallback permission extraction using cryptography."""
        try:
            with open(cert_path, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read())

            # Look for custom permission extension
            try:
                permission_extension = cert.extensions.get_extension_for_oid(
                    x509.ObjectIdentifier("1.3.6.1.4.1.99999.2")  # Custom OID for permissions
                )
                if permission_extension:
                    # Parse permissions from extension value
                    permissions_str = permission_extension.value.value.decode('utf-8')
                    return [perm.strip() for perm in permissions_str.split(',') if perm.strip()]
            except x509.ExtensionNotFound:
                pass

            return []

        except Exception as e:
            logger.error(f"Failed to extract permissions from certificate (fallback): {e}")
            return []
