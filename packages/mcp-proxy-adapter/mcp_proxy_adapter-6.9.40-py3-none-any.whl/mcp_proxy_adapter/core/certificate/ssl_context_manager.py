"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

SSL context management utilities for MCP Proxy Adapter.
"""

import ssl
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SSLContextManager:
    """Manager for SSL contexts."""

    @staticmethod
    def create_ssl_context(
        cert_file: Optional[str] = None,
        key_file: Optional[str] = None,
        ca_cert_file: Optional[str] = None,
        verify_mode: int = ssl.CERT_NONE,
        check_hostname: bool = False,
    ) -> ssl.SSLContext:
        """
        Create SSL context for server or client.

        Args:
            cert_file: Path to certificate file
            key_file: Path to private key file
            ca_cert_file: Path to CA certificate file
            verify_mode: SSL verification mode
            check_hostname: Whether to check hostname

        Returns:
            SSL context
        """
        try:
            # Create SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = check_hostname
            ssl_context.verify_mode = verify_mode

            # Load certificate and key if provided
            if cert_file and key_file:
                if not Path(cert_file).exists():
                    raise FileNotFoundError(f"Certificate file not found: {cert_file}")
                if not Path(key_file).exists():
                    raise FileNotFoundError(f"Key file not found: {key_file}")
                
                ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file)

            # Load CA certificate if provided
            if ca_cert_file:
                if not Path(ca_cert_file).exists():
                    raise FileNotFoundError(f"CA certificate file not found: {ca_cert_file}")
                ssl_context.load_verify_locations(cafile=ca_cert_file)

            return ssl_context

        except Exception as e:
            logger.error(f"Failed to create SSL context: {e}")
            raise
