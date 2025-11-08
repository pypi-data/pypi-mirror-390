"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

File validation utilities for MCP Proxy Adapter configuration validation.
"""

import os
import ssl
from typing import Dict, Any, List

from .validation_result import ValidationResult


class FileValidator:
    """Validator for file-related configuration settings."""

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

    def _is_file_required_for_enabled_features(self, file_key: str) -> bool:
        """Check if a file is required based on enabled features."""
        # SSL files are required if SSL is enabled
        if file_key.startswith("ssl.") or file_key.startswith("transport.ssl."):
            return self._get_nested_value_safe("ssl.enabled", False)
        
        # Proxy registration files are required if proxy registration is enabled
        if file_key.startswith("proxy_registration."):
            return self._get_nested_value_safe("proxy_registration.enabled", False)
        
        # Log directory is required if logging is enabled
        if file_key == "logging.log_dir":
            return self._get_nested_value_safe("logging.enabled", True)
        
        # Command directories are required if commands are enabled
        if file_key.startswith("commands."):
            return self._get_nested_value_safe("commands.enabled", True)
        
        # Security files are required if security is enabled
        if file_key.startswith("security."):
            return self._get_nested_value_safe("security.enabled", False)
        
        return False

    def validate_file_existence(self) -> List[ValidationResult]:
        """
        Validate that referenced files exist.

        Returns:
            List of validation results
        """
        self.validation_results = []
        
        # Check SSL certificate files if SSL is enabled
        if self._get_nested_value_safe("ssl.enabled", False):
            cert_file = self._get_nested_value_safe("ssl.cert_file")
            key_file = self._get_nested_value_safe("ssl.key_file")
            
            if cert_file and not os.path.exists(cert_file):
                self.validation_results.append(ValidationResult(
                    level="error",
                    message=f"SSL certificate file not found: {cert_file}",
                    section="ssl",
                    key="cert_file",
                    suggestion=f"Create or fix path to certificate file"
                ))
            
            if key_file and not os.path.exists(key_file):
                self.validation_results.append(ValidationResult(
                    level="error",
                    message=f"SSL key file not found: {key_file}",
                    section="ssl",
                    key="key_file",
                    suggestion=f"Create or fix path to key file"
                ))
        
        # Check proxy registration certificate files if proxy registration is enabled
        if self._get_nested_value_safe("proxy_registration.enabled", False):
            proxy_cert = self._get_nested_value_safe("proxy_registration.certificate.cert_file")
            proxy_key = self._get_nested_value_safe("proxy_registration.certificate.key_file")
            
            if proxy_cert and not os.path.exists(proxy_cert):
                self.validation_results.append(ValidationResult(
                    level="warning",
                    message=f"Proxy registration certificate file not found: {proxy_cert}",
                    section="proxy_registration.certificate",
                    key="cert_file",
                    suggestion=f"Create or fix path to certificate file"
                ))
            
            if proxy_key and not os.path.exists(proxy_key):
                self.validation_results.append(ValidationResult(
                    level="warning",
                    message=f"Proxy registration key file not found: {proxy_key}",
                    section="proxy_registration.certificate",
                    key="key_file",
                    suggestion=f"Create or fix path to key file"
                ))
        
        return self.validation_results
