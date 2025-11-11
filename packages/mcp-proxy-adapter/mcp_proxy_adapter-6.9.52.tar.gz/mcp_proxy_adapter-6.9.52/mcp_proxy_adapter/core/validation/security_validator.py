"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Security validation utilities for MCP Proxy Adapter configuration validation.
"""

import os
from typing import Dict, List, Any

from .validation_result import ValidationResult


class SecurityValidator:
    """Validator for security-related configuration settings."""

    def __init__(self, config_data: Dict[str, Any]):
        self.config_data = config_data
        self.validation_results: List[ValidationResult] = []





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

    def _has_nested_key(self, key: str) -> bool:
        """Check if a nested key exists in configuration."""
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return False
        
        return True

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL has valid format."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False

    def validate_security_consistency(self) -> List[ValidationResult]:
        """
        Validate security configuration consistency.

        Returns:
            List of validation results
        """
        self.validation_results = []
        # Basic consistency checks can be added here
        return self.validation_results

    def validate_ssl_configuration(self) -> List[ValidationResult]:
        """
        Validate SSL configuration.

        Returns:
            List of validation results
        """
        self.validation_results = []
        
        ssl_config = self._get_nested_value_safe("ssl", {})
        if ssl_config.get("enabled", False):
            if not ssl_config.get("cert_file"):
                self.validation_results.append(ValidationResult(
                    level="error",
                    message="SSL is enabled but cert_file is not specified",
                    section="ssl",
                    key="cert_file",
                    suggestion="Specify ssl.cert_file"
                ))
            if not ssl_config.get("key_file"):
                self.validation_results.append(ValidationResult(
                    level="error",
                    message="SSL is enabled but key_file is not specified",
                    section="ssl",
                    key="key_file",
                    suggestion="Specify ssl.key_file"
                ))
        
        return self.validation_results

    def validate_roles_configuration(self) -> List[ValidationResult]:
        """
        Validate roles configuration.

        Returns:
            List of validation results
        """
        self.validation_results = []
        # Roles validation can be added here
        return self.validation_results

    def validate_proxy_registration(self) -> List[ValidationResult]:
        """
        Validate proxy registration configuration.

        Returns:
            List of validation results
        """
        self.validation_results = []
        
        # Validate legacy proxy_registration format
        proxy_config = self._get_nested_value_safe("proxy_registration", {})
        if proxy_config.get("enabled", False):
            if not proxy_config.get("proxy_url"):
                self.validation_results.append(ValidationResult(
                    level="error",
                    message="Proxy registration is enabled but proxy_url is not specified",
                    section="proxy_registration",
                    key="proxy_url",
                    suggestion="Specify proxy_registration.proxy_url"
                ))
            elif not self._is_valid_url(proxy_config.get("proxy_url", "")):
                self.validation_results.append(ValidationResult(
                    level="error",
                    message=f"Invalid proxy URL format: {proxy_config.get('proxy_url')}",
                    section="proxy_registration",
                    key="proxy_url",
                    suggestion="Use a valid URL format (e.g., http://host:port)"
                ))
        
        # Validate new registration format (SimpleConfig)
        registration_config = self._get_nested_value_safe("registration", {})
        if registration_config.get("enabled", False):
            # Check if register_url is provided or can be generated
            register_url = registration_config.get("register_url")
            if not register_url:
                # Check if we can generate it from host/port/protocol/endpoint
                host = registration_config.get("host")
                port = registration_config.get("port")
                protocol = registration_config.get("protocol", "http")
                register_endpoint = registration_config.get("register_endpoint", "/register")
                if host and port:
                    # Can be generated, but warn that explicit URL is preferred
                    self.validation_results.append(ValidationResult(
                        level="warning",
                        message="register_url not specified, will be auto-generated from host/port/endpoint",
                        section="registration",
                        key="register_url",
                        suggestion="Specify registration.register_url explicitly for clarity"
                    ))
                else:
                    self.validation_results.append(ValidationResult(
                        level="error",
                        message="registration.enabled=true but register_url cannot be determined (missing host/port)",
                        section="registration",
                        key="register_url",
                        suggestion="Specify registration.register_url or registration.host/port"
                    ))
            elif not self._is_valid_url(register_url):
                self.validation_results.append(ValidationResult(
                    level="error",
                    message=f"Invalid register_url format: {register_url}",
                    section="registration",
                    key="register_url",
                    suggestion="Use a valid URL format (e.g., http://host:port/register)"
                ))
            
            # Check heartbeat URL
            heartbeat_config = registration_config.get("heartbeat", {})
            heartbeat_url = heartbeat_config.get("url") if isinstance(heartbeat_config, dict) else None
            if not heartbeat_url:
                # Check if we can generate it
                host = registration_config.get("host")
                port = registration_config.get("port")
                protocol = registration_config.get("protocol", "http")
                if host and port:
                    # Can be generated, but warn
                    self.validation_results.append(ValidationResult(
                        level="warning",
                        message="heartbeat.url not specified, will be auto-generated",
                        section="registration.heartbeat",
                        key="url",
                        suggestion="Specify registration.heartbeat.url explicitly (e.g., http://host:port/proxy/heartbeat)"
                    ))
                else:
                    self.validation_results.append(ValidationResult(
                        level="error",
                        message="registration.enabled=true but heartbeat.url cannot be determined (missing host/port)",
                        section="registration.heartbeat",
                        key="url",
                        suggestion="Specify registration.heartbeat.url or registration.host/port"
                    ))
            elif not self._is_valid_url(heartbeat_url):
                self.validation_results.append(ValidationResult(
                    level="error",
                    message=f"Invalid heartbeat.url format: {heartbeat_url}",
                    section="registration.heartbeat",
                    key="url",
                    suggestion="Use a valid URL format (e.g., http://host:port/proxy/heartbeat)"
                ))
        
        return self.validation_results
