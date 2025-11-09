"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Protocol validation utilities for MCP Proxy Adapter configuration validation.
"""

import re
from typing import Dict, List, Any

from .validation_result import ValidationResult


class ProtocolValidator:
    """Validator for protocol-related configuration settings."""

    def __init__(self, config_data: Dict[str, Any]):
        self.config_data = config_data
        self.validation_results: List[ValidationResult] = []

    def _validate_https_requirements(self) -> None:
        """Validate HTTPS-specific requirements."""
        # Check server section for certificates (SimpleConfig format)
        server_config = self._get_nested_value_safe("server", {})

        # Check for required SSL files in server section
        if not server_config.get("cert_file"):
            self.validation_results.append(
                ValidationResult(
                    level="error",
                    message="HTTPS protocol requires SSL certificate file",
                    section="server",
                    key="cert_file",
                    suggestion="Specify server.cert_file",
                )
            )

        if not server_config.get("key_file"):
            self.validation_results.append(
                ValidationResult(
                    level="error",
                    message="HTTPS protocol requires SSL key file",
                    section="server",
                    key="key_file",
                    suggestion="Specify server.key_file",
                )
            )

    def _validate_mtls_requirements(self) -> None:
        """Validate mTLS-specific requirements."""
        # mTLS requires HTTPS
        self._validate_https_requirements()

        # Check server section for certificates (SimpleConfig format)
        server_config = self._get_nested_value_safe("server", {})
        transport_config = self._get_nested_value_safe("transport", {})

        # For mTLS server, we need:
        # - Server cert/key (already checked by _validate_https_requirements)
        # - CA cert for verifying client certificates
        # - verify_client enabled

        # Check for CA certificate (needed for client certificate verification)
        if not server_config.get("ca_cert_file"):
            self.validation_results.append(
                ValidationResult(
                    level="error",
                    message="mTLS protocol requires CA certificate for client verification",
                    section="server",
                    key="ca_cert_file",
                    suggestion="Specify server.ca_cert_file for client certificate verification",
                )
            )

        # Check for client verification
        if not transport_config.get("verify_client", False):
            self.validation_results.append(
                ValidationResult(
                    level="warning",
                    message="mTLS protocol should have client verification enabled",
                    section="transport",
                    key="verify_client",
                    suggestion="Set transport.verify_client to true",
                )
            )

        # Note: client_cert and client_key are NOT required for mTLS server
        # They are only needed for client/registration configuration when connecting TO a proxy

    def _validate_feature_flags(self) -> None:
        """Validate feature flags based on protocol."""
        protocol = self._get_nested_value_safe("server.protocol", "http")
        server_config = self._get_nested_value_safe("server", {})

        # Check if features are compatible with protocol
        if protocol == "http":
            # HTTP doesn't support SSL features
            if server_config.get("cert_file") or server_config.get("key_file"):
                self.validation_results.append(
                    ValidationResult(
                        level="warning",
                        message="SSL certificates are configured but protocol is HTTP. Consider using HTTPS",
                        section="server",
                        suggestion="Change protocol to https or remove certificate configuration",
                    )
                )

        # Check transport configuration
        transport_config = self._get_nested_value_safe("transport", {})
        if transport_config:
            verify_client = transport_config.get("verify_client", False)
            if verify_client and protocol == "http":
                self.validation_results.append(
                    ValidationResult(
                        level="warning",
                        message="Client verification is enabled but protocol is HTTP",
                        section="transport",
                        key="verify_client",
                        suggestion="Change protocol to https or mtls, or disable client verification",
                    )
                )

    def _validate_server_section(self) -> None:
        """Validate server section requirements."""
        server_config = self.config_data.get("server", {})

        # Check required fields
        if "host" not in server_config:
            self.validation_results.append(
                ValidationResult(
                    level="error",
                    message="Server host is required",
                    section="server",
                    key="host",
                    suggestion="Add host field to server section",
                )
            )

        if "port" not in server_config:
            self.validation_results.append(
                ValidationResult(
                    level="error",
                    message="Server port is required",
                    section="server",
                    key="port",
                    suggestion="Add port field to server section",
                )
            )

        # Validate port number
        port = server_config.get("port")
        if port is not None:
            if not isinstance(port, int) or not (1 <= port <= 65535):
                self.validation_results.append(
                    ValidationResult(
                        level="error",
                        message=f"Invalid port number: {port}. Must be between 1 and 65535",
                        section="server",
                        key="port",
                    )
                )

        # Validate host format
        host = server_config.get("host")
        if host is not None:
            if not self._is_valid_host(host):
                self.validation_results.append(
                    ValidationResult(
                        level="error",
                        message=f"Invalid host format: {host}",
                        section="server",
                        key="host",
                        suggestion="Use a valid hostname or IP address",
                    )
                )

    def _is_valid_host(self, host: str) -> bool:
        """Check if host has valid format."""
        # Check for localhost
        if host in ["localhost", "127.0.0.1", "::1", "0.0.0.0"]:
            return True

        # Check for IP address
        ip_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        if re.match(ip_pattern, host):
            # Validate IP address ranges
            parts = host.split(".")
            return all(0 <= int(part) <= 255 for part in parts)

        # Check for hostname (basic validation)
        hostname_pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$"
        return bool(re.match(hostname_pattern, host))

    def _get_nested_value_safe(self, key: str, default: Any = None) -> Any:
        """Safely get a nested value from configuration."""
        keys = key.split(".")
        value = self.config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value
