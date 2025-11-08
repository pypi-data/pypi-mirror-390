"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Simple configuration generator for MCP Proxy Adapter.
"""

from __future__ import annotations

from typing import Optional

from .simple_config import (
    SimpleConfig,
    SimpleConfigModel,
    ServerConfig,
    ProxyClientConfig,
    AuthConfig,
)


class SimpleConfigGenerator:
    """Generate minimal configuration according to the plan."""

    def generate(
        self,
        protocol: str,
        with_proxy: bool = False,
        out_path: str = "config.json",
        server_host: Optional[str] = None,
        server_port: Optional[int] = None,
        server_cert_file: Optional[str] = None,
        server_key_file: Optional[str] = None,
        server_ca_cert_file: Optional[str] = None,
        proxy_host: Optional[str] = None,
        proxy_port: Optional[int] = None,
        proxy_cert_file: Optional[str] = None,
        proxy_key_file: Optional[str] = None,
        proxy_ca_cert_file: Optional[str] = None,
    ) -> str:
        """
        Generate configuration with optional custom parameters.

        Args:
            protocol: Server protocol (http, https, mtls)
            with_proxy: Enable proxy registration
            out_path: Output file path
            server_host: Server host (default: 0.0.0.0)
            server_port: Server port (default: 8080)
            server_cert_file: Server certificate file path
            server_key_file: Server key file path
            server_ca_cert_file: Server CA certificate file path
            proxy_host: Proxy host (default: localhost)
            proxy_port: Proxy port (default: 3005)
            proxy_cert_file: Proxy client certificate file path
            proxy_key_file: Proxy client key file path
            proxy_ca_cert_file: Proxy CA certificate file path
        """
        # Server configuration
        server = ServerConfig(
            host=server_host or "0.0.0.0", port=server_port or 8080, protocol=protocol
        )
        if protocol in ("https", "mtls"):
            server.cert_file = server_cert_file or "./certs/server.crt"
            server.key_file = server_key_file or "./certs/server.key"
        if protocol == "mtls":
            server.ca_cert_file = server_ca_cert_file or "./certs/ca.crt"

        # Proxy configuration
        proxy = ProxyClientConfig(enabled=with_proxy)
        if with_proxy:
            # NOTE: proxy.protocol indicates the SERVER's protocol, not the proxy's protocol
            # The proxy itself typically runs on HTTP (for test proxy) or may have its own protocol
            # This field is used to determine if client certificates are needed for proxy connection
            # (if proxy itself uses HTTPS/mTLS, which is not the case for test proxy)
            proxy.protocol = protocol
            proxy.host = proxy_host or "localhost"
            proxy.port = proxy_port or 3005
            # Client certificates for proxy connection (only if proxy itself uses HTTPS/mTLS)
            # For test proxy (HTTP), these are not used but may be set for consistency
            if protocol in ("https", "mtls"):
                proxy.cert_file = proxy_cert_file or "./certs/client.crt"
                proxy.key_file = proxy_key_file or "./certs/client.key"
            if protocol == "mtls":
                proxy.ca_cert_file = proxy_ca_cert_file or "./certs/ca.crt"
            # Explicitly set registration.auto_on_startup when proxy is enabled
            # Note: enabled controls client availability, registration.auto_on_startup controls auto-registration
            proxy.registration.auto_on_startup = True

        auth = AuthConfig(use_token=False, use_roles=False, tokens={}, roles={})

        cfg = SimpleConfig()
        cfg.model = SimpleConfigModel(server=server, proxy_client=proxy, auth=auth)
        cfg.save(out_path)
        return out_path
