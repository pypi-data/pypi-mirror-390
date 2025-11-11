"""
SSL Utilities Module

This module provides utilities for SSL/TLS configuration and certificate validation.
Integrates with AuthValidator from Phase 0 for certificate validation.
Supports CRL (Certificate Revocation List) validation.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
Version: 1.0.0
"""

import ssl
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from .auth_validator import AuthValidator
from .crl_utils import CRLManager

logger = logging.getLogger(__name__)


class SSLUtils:
    """
    SSL utilities for creating SSL contexts and validating certificates.
    """

    # TLS version mapping
    TLS_VERSIONS = {
        "1.0": ssl.TLSVersion.TLSv1,
        "1.1": ssl.TLSVersion.TLSv1_1,
        "1.2": ssl.TLSVersion.TLSv1_2,
        "1.3": ssl.TLSVersion.TLSv1_3,
    }

    # Cipher suite mapping
    CIPHER_SUITES = {
        "TLS_AES_256_GCM_SHA384": "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256": "TLS_CHACHA20_POLY1305_SHA256",
        "TLS_AES_128_GCM_SHA256": "TLS_AES_128_GCM_SHA256",
        "ECDHE-RSA-AES256-GCM-SHA384": "ECDHE-RSA-AES256-GCM-SHA384",
        "ECDHE-RSA-AES128-GCM-SHA256": "ECDHE-RSA-AES128-GCM-SHA256",
        "ECDHE-RSA-CHACHA20-POLY1305": "ECDHE-RSA-CHACHA20-POLY1305",
    }

    @staticmethod

    @staticmethod
    def validate_certificate(
        cert_file: str, crl_config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Validate certificate using AuthValidator and optional CRL check.

        Args:
            cert_file: Path to certificate file
            crl_config: CRL configuration dictionary (optional)

        Returns:
            True if certificate is valid, False otherwise
        """
        try:
            validator = AuthValidator()
            result = validator.validate_certificate(cert_file)
            if not result.is_valid:
                return False

            # Check CRL if configured
            if crl_config:
                try:
                    crl_manager = CRLManager(crl_config)
                    if crl_manager.is_certificate_revoked(cert_file):
                        get_global_logger().warning(
                            f"Certificate is revoked according to CRL: {cert_file}"
                        )
                        return False
                except Exception as e:
                    get_global_logger().error(f"CRL check failed: {e}")
                    # For security, consider certificate invalid if CRL check fails
                    return False

            return True
        except Exception as e:
            get_global_logger().error(f"Certificate validation failed: {e}")
            return False

    @staticmethod
    def setup_cipher_suites(context: ssl.SSLContext, cipher_suites: List[str]) -> None:
        """
        Setup cipher suites for SSL context.

        Args:
            context: SSL context to configure
            cipher_suites: List of cipher suite names
        """
        if not cipher_suites:
            return

        # Convert cipher suite names to actual cipher suite strings
        actual_ciphers = []
        for cipher_name in cipher_suites:
            if cipher_name in SSLUtils.CIPHER_SUITES:
                actual_ciphers.append(SSLUtils.CIPHER_SUITES[cipher_name])
            else:
                get_global_logger().warning(f"Unknown cipher suite: {cipher_name}")

        if actual_ciphers:
            try:
                context.set_ciphers(":".join(actual_ciphers))
                get_global_logger().info(f"Cipher suites configured: {actual_ciphers}")
            except ssl.SSLError as e:
                get_global_logger().error(f"Failed to set cipher suites: {e}")

    @staticmethod
    def setup_tls_versions(
        context: ssl.SSLContext, min_version: str, max_version: str
    ) -> None:
        """
        Setup TLS version range for SSL context.

        Args:
            context: SSL context to configure
            min_version: Minimum TLS version
            max_version: Maximum TLS version
        """
        try:
            min_tls = SSLUtils.TLS_VERSIONS.get(min_version)
            max_tls = SSLUtils.TLS_VERSIONS.get(max_version)

            if min_tls and max_tls:
                context.minimum_version = min_tls
                context.maximum_version = max_tls
                get_global_logger().info(f"TLS versions configured: {min_version} - {max_version}")
            else:
                get_global_logger().warning(
                    f"Invalid TLS version range: {min_version} - {max_version}"
                )
        except Exception as e:
            get_global_logger().error(f"Failed to set TLS versions: {e}")

    @staticmethod
    def create_ssl_context(
        cert_file: Optional[str] = None,
        key_file: Optional[str] = None,
        ca_file: Optional[str] = None,
        verify_mode: int = ssl.CERT_REQUIRED,
        check_hostname: bool = True,
    ) -> ssl.SSLContext:
        """Create SSL context with proper configuration."""
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = check_hostname
        context.verify_mode = verify_mode
        
        if cert_file and key_file:
            context.load_cert_chain(cert_file, key_file)
        
        if ca_file:
            context.load_verify_locations(ca_file)
            
        return context
