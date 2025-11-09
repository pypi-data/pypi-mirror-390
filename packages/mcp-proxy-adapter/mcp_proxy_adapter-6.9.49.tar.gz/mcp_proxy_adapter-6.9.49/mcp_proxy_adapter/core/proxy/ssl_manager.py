"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

SSL management for proxy registration.
"""

import ssl
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from mcp_proxy_adapter.core.logging import get_global_logger


class SSLManager:
    """Manager for SSL connections in proxy registration."""

    def __init__(self, client_security, registration_config: Dict[str, Any], config: Dict[str, Any], proxy_url: str):
        """
        Initialize SSL manager.

        Args:
            client_security: Client security manager instance
            registration_config: Registration configuration
            config: Application configuration
            proxy_url: Proxy server URL
        """
        self.client_security = client_security
        self.registration_config = registration_config
        self.config = config
        self.proxy_url = proxy_url
        self.logger = get_global_logger()

    def create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """
        Create SSL context for secure connections using registration SSL configuration.

        Returns:
            SSL context or None if SSL not needed
        """
        self.logger.debug("_create_ssl_context called")
        
        # Decide SSL strictly by proxy URL scheme: use SSL only for https proxy URLs
        try:
            scheme = urlparse(self.proxy_url).scheme if self.proxy_url else "http"
            if scheme.lower() != "https":
                self.logger.debug("Proxy URL is HTTP, skipping SSL context creation for registration")
                return None
        except Exception:
            self.logger.debug("Failed to parse proxy_url, assuming HTTP and skipping SSL context")
            return None
            
        if not self.client_security:
            self.logger.debug("SSL context creation failed: client_security is None")
            return None

        try:
            # Check if SSL is enabled for registration
            cert_config = self.registration_config.get("certificate", {})
            ssl_config = self.registration_config.get("ssl", {})

            # FALLBACK: if no explicit registration SSL/certs provided, reuse global SSL config
            if not cert_config and not ssl_config:
                global_ssl = self.config.get("security", {}).get("ssl", {}) or self.config.get("ssl", {})
                if global_ssl:
                    # Map global ssl to registration-style configs
                    mapped_cert = {}
                    if global_ssl.get("cert_file") and global_ssl.get("key_file"):
                        mapped_cert = {
                            "cert_file": global_ssl.get("cert_file"),
                            "key_file": global_ssl.get("key_file"),
                        }
                    mapped_ssl = {}
                    if global_ssl.get("ca_cert"):
                        mapped_ssl["ca_cert"] = global_ssl.get("ca_cert")
                    if global_ssl.get("verify_client") is not None:
                        mapped_ssl["verify_mode"] = (
                            "CERT_REQUIRED" if global_ssl.get("verify_client") else "CERT_NONE"
                        )
                    cert_config = mapped_cert
                    ssl_config = mapped_ssl

            # Use client security manager to create SSL context
            if cert_config or ssl_config:
                ssl_context = self.client_security.create_ssl_context(
                    cert_config=cert_config,
                    ssl_config=ssl_config
                )
                if ssl_context:
                    self.logger.debug("SSL context created successfully for registration")
                    return ssl_context
                else:
                    self.logger.warning("Failed to create SSL context for registration")
                    return None
            else:
                self.logger.debug("No SSL configuration found for registration")
                return None

        except Exception as e:
            self.logger.error(f"Error creating SSL context for registration: {e}")
            return None
