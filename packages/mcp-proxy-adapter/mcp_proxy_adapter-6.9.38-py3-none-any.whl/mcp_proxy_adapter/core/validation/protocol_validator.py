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
        ssl_config = self._get_nested_value_safe("ssl", {})
        
        if not ssl_config.get("enabled", False):
            self.validation_results.append(ValidationResult(
                level="error",
                message="HTTPS protocol requires SSL to be enabled",
                section="ssl",
                suggestion="Set ssl.enabled to true"
            ))
        
        # Check for required SSL files
        if not ssl_config.get("cert_file"):
            self.validation_results.append(ValidationResult(
                level="error",
                message="HTTPS protocol requires SSL certificate file",
                section="ssl",
                key="cert_file",
                suggestion="Specify ssl.cert_file"
            ))
        
        if not ssl_config.get("key_file"):
            self.validation_results.append(ValidationResult(
                level="error",
                message="HTTPS protocol requires SSL key file",
                section="ssl",
                key="key_file",
                suggestion="Specify ssl.key_file"
            ))

    def _validate_mtls_requirements(self) -> None:
        """Validate mTLS-specific requirements."""
        # mTLS requires HTTPS
        self._validate_https_requirements()
        
        ssl_config = self._get_nested_value_safe("ssl", {})
        
        # For mTLS server, we need:
        # - Server cert/key (already checked by _validate_https_requirements)
        # - CA cert for verifying client certificates
        # - verify_client enabled
        
        # Check for CA certificate (needed for client certificate verification)
        if not ssl_config.get("ca_cert"):
            self.validation_results.append(ValidationResult(
                level="warning",
                message="mTLS protocol should have CA certificate for client verification",
                section="ssl",
                key="ca_cert",
                suggestion="Specify ssl.ca_cert for client certificate verification"
            ))
        
        # Check for client verification
        if not ssl_config.get("verify_client", False):
            self.validation_results.append(ValidationResult(
                level="warning",
                message="mTLS protocol should have client verification enabled",
                section="ssl",
                key="verify_client",
                suggestion="Set ssl.verify_client to true"
            ))
        
        # Note: client_cert and client_key are NOT required for mTLS server
        # They are only needed for proxy_client configuration when connecting TO a proxy

    def _validate_feature_flags(self) -> None:
        """Validate feature flags based on protocol."""
        protocol = self._get_nested_value_safe("server.protocol", "http")
        
        # Check if features are compatible with protocol
        if protocol == "http":
            # HTTP doesn't support SSL features
            if self._get_nested_value_safe("ssl.enabled", False):
                self.validation_results.append(ValidationResult(
                    level="warning",
                    message="SSL is enabled but protocol is HTTP. Consider using HTTPS",
                    section="ssl",
                    suggestion="Change protocol to https or disable SSL"
                ))
        
        # Check transport configuration
        transport_config = self._get_nested_value_safe("transport", {})
        if transport_config:
            transport_ssl = transport_config.get("ssl", {})
            if transport_ssl.get("enabled", False) and protocol == "http":
                self.validation_results.append(ValidationResult(
                    level="warning",
                    message="Transport SSL is enabled but protocol is HTTP",
                    section="transport.ssl",
                    suggestion="Change protocol to https or disable transport SSL"
                ))

    def _validate_server_section(self) -> None:
        """Validate server section requirements."""
        server_config = self.config_data.get("server", {})
        
        # Check required fields
        if "host" not in server_config:
            self.validation_results.append(ValidationResult(
                level="error",
                message="Server host is required",
                section="server",
                key="host",
                suggestion="Add host field to server section"
            ))
        
        if "port" not in server_config:
            self.validation_results.append(ValidationResult(
                level="error",
                message="Server port is required",
                section="server",
                key="port",
                suggestion="Add port field to server section"
            ))
        
        # Validate port number
        port = server_config.get("port")
        if port is not None:
            if not isinstance(port, int) or not (1 <= port <= 65535):
                self.validation_results.append(ValidationResult(
                    level="error",
                    message=f"Invalid port number: {port}. Must be between 1 and 65535",
                    section="server",
                    key="port"
                ))
        
        # Validate host format
        host = server_config.get("host")
        if host is not None:
            if not self._is_valid_host(host):
                self.validation_results.append(ValidationResult(
                    level="error",
                    message=f"Invalid host format: {host}",
                    section="server",
                    key="host",
                    suggestion="Use a valid hostname or IP address"
                ))

    def _is_valid_host(self, host: str) -> bool:
        """Check if host has valid format."""
        # Check for localhost
        if host in ["localhost", "127.0.0.1", "::1", "0.0.0.0"]:
            return True
        
        # Check for IP address
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ip_pattern, host):
            # Validate IP address ranges
            parts = host.split('.')
            return all(0 <= int(part) <= 255 for part in parts)
        
        # Check for hostname (basic validation)
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(hostname_pattern, host))

    def _get_nested_value_safe(self, key: str, default: Any = None) -> Any:
        """Safely get a nested value from configuration."""
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
