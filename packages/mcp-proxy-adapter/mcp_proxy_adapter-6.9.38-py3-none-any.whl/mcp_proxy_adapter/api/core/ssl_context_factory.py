"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

SSL context factory for MCP Proxy Adapter API.
"""

import ssl
from pathlib import Path
from typing import Any, Dict, Optional

from mcp_proxy_adapter.core.logging import get_global_logger
from mcp_proxy_adapter.core.ssl_utils import SSLUtils


class SSLContextFactory:
    """Factory for creating SSL contexts."""

    def __init__(self):
        """Initialize SSL context factory."""
        self.logger = get_global_logger()

    def create_ssl_context(
        self,
        app_config: Optional[Dict[str, Any]] = None
    ) -> Optional[ssl.SSLContext]:
        """
        Create SSL context based on configuration.

        Args:
            app_config: Application configuration dictionary (optional)

        Returns:
            SSL context if SSL is enabled and properly configured, None otherwise
        """
        from mcp_proxy_adapter.config import config
        
        current_config = app_config if app_config is not None else config.get_all()

        # Check SSL configuration from new structure
        protocol = current_config.get("server", {}).get("protocol", "http")
        verify_client = current_config.get("transport", {}).get("verify_client", False)
        ssl_enabled = protocol in ["https", "mtls"] or verify_client

        if not ssl_enabled:
            self.logger.info("SSL is disabled in configuration")
            return None

        # Get certificate paths from configuration
        cert_file = current_config.get("transport", {}).get("cert_file")
        key_file = current_config.get("transport", {}).get("key_file")
        ca_cert = current_config.get("transport", {}).get("ca_cert")
        
        # Convert relative paths to absolute paths
        if cert_file and not Path(cert_file).is_absolute():
            project_root = Path(__file__).parent.parent.parent.parent
            cert_file = str(project_root / cert_file)
        if key_file and not Path(key_file).is_absolute():
            project_root = Path(__file__).parent.parent.parent.parent
            key_file = str(project_root / key_file)
        if ca_cert and not Path(ca_cert).is_absolute():
            project_root = Path(__file__).parent.parent.parent.parent
            ca_cert = str(project_root / ca_cert)

        if not cert_file or not key_file:
            self.logger.warning("SSL enabled but certificate or key file not specified")
            return None

        try:
            # Create SSL context using SSLUtils
            ssl_context = SSLUtils.create_ssl_context(
                cert_file=cert_file,
                key_file=key_file,
                ca_cert=ca_cert,
                verify_client=current_config.get("transport", {}).get("verify_client", False),
                cipher_suites=[],
                min_tls_version="1.2",
                max_tls_version="1.3",
            )

            self.logger.info(
                f"SSL context created successfully for mode: https_only"
            )
            return ssl_context

        except Exception as e:
            self.logger.error(f"Failed to create SSL context: {e}")
            return None
