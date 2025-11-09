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
    ClientConfig,
    RegistrationConfig,
    AuthConfig,
)


class SimpleConfigGenerator:
    """Generate minimal configuration according to the plan."""

    def generate(
        self,
        protocol: str,
        with_proxy: bool = False,
        out_path: str = "config.json",
        # Server parameters
        server_host: Optional[str] = None,
        server_port: Optional[int] = None,
        server_cert_file: Optional[str] = None,
        server_key_file: Optional[str] = None,
        server_ca_cert_file: Optional[str] = None,
        server_crl_file: Optional[str] = None,
        # Client parameters
        client_enabled: bool = False,
        client_protocol: Optional[str] = None,
        client_cert_file: Optional[str] = None,
        client_key_file: Optional[str] = None,
        client_ca_cert_file: Optional[str] = None,
        client_crl_file: Optional[str] = None,
        # Registration parameters
        registration_host: Optional[str] = None,
        registration_port: Optional[int] = None,
        registration_protocol: Optional[str] = None,
        registration_cert_file: Optional[str] = None,
        registration_key_file: Optional[str] = None,
        registration_ca_cert_file: Optional[str] = None,
        registration_crl_file: Optional[str] = None,
    ) -> str:
        """
        Generate configuration with optional custom parameters.
        
        Args:
            protocol: Server protocol (http, https, mtls)
            with_proxy: Enable proxy registration (deprecated, use registration parameters)
            out_path: Output file path
            # Server parameters
            server_host: Server host (default: 0.0.0.0)
            server_port: Server port (default: 8080)
            server_cert_file: Server certificate file path
            server_key_file: Server key file path
            server_ca_cert_file: Server CA certificate file path
            server_crl_file: Server CRL file path
            # Client parameters
            client_enabled: Enable client configuration
            client_protocol: Client protocol (http, https, mtls)
            client_cert_file: Client certificate file path
            client_key_file: Client key file path
            client_ca_cert_file: Client CA certificate file path
            client_crl_file: Client CRL file path
            # Registration parameters
            registration_host: Registration proxy host (default: localhost)
            registration_port: Registration proxy port (default: 3005)
            registration_protocol: Registration protocol (http, https, mtls)
            registration_cert_file: Registration certificate file path
            registration_key_file: Registration key file path
            registration_ca_cert_file: Registration CA certificate file path
            registration_crl_file: Registration CRL file path
        """
        # Server configuration
        server = ServerConfig(
            host=server_host or "0.0.0.0", port=server_port or 8080, protocol=protocol
        )
        if protocol in ("https", "mtls"):
            server.cert_file = server_cert_file or "./certs/server.crt"
            server.key_file = server_key_file or "./certs/server.key"
        # For mtls: CA is required if use_system_ca=False (default), optional if use_system_ca=True
        # Only set if explicitly provided
        if protocol == "mtls" and server_ca_cert_file:
            server.ca_cert_file = server_ca_cert_file
        if server_crl_file:
            server.crl_file = server_crl_file
        # use_system_ca defaults to False (only CA from config is used by default)

        # Client configuration
        client = ClientConfig(enabled=client_enabled)
        if client_enabled:
            client.protocol = client_protocol or protocol
            if client.protocol in ("https", "mtls"):
                client.cert_file = client_cert_file or "./certs/client.crt"
                client.key_file = client_key_file or "./certs/client.key"
            if client.protocol == "mtls" and client_ca_cert_file:
                client.ca_cert_file = client_ca_cert_file
            if client_crl_file:
                client.crl_file = client_crl_file

        # Registration configuration
        registration = RegistrationConfig(enabled=with_proxy)
        if with_proxy:
            registration.host = registration_host or "localhost"
            registration.port = registration_port or 3005
            registration.protocol = registration_protocol or "http"
            # Client certificates for proxy connection (only if proxy itself uses HTTPS/mTLS)
            if registration.protocol in ("https", "mtls"):
                registration.cert_file = registration_cert_file or "./certs/registration.crt"
                registration.key_file = registration_key_file or "./certs/registration.key"
            if registration.protocol == "mtls" and registration_ca_cert_file:
                registration.ca_cert_file = registration_ca_cert_file
            if registration_crl_file:
                registration.crl_file = registration_crl_file
            registration.auto_on_startup = True

        auth = AuthConfig(use_token=False, use_roles=False, tokens={}, roles={})

        cfg = SimpleConfig()
        cfg.model = SimpleConfigModel(server=server, client=client, registration=registration, auth=auth)
        cfg.save(out_path)
        return out_path
