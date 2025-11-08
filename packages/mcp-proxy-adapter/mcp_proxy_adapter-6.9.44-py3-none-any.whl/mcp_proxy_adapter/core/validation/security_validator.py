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
        
        return self.validation_results
