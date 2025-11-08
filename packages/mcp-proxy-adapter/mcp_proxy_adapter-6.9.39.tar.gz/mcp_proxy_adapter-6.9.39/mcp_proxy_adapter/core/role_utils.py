"""
Role Utilities

This module provides utilities for working with roles extracted from certificates.
Includes functions for role extraction, comparison, validation, and normalization.

Author: MCP Proxy Adapter Team
Version: 1.0.0
"""

import logging
from typing import List


class RoleUtils:
    """
    Utilities for working with roles from certificates.

    Provides methods for extracting, comparing, validating, and normalizing roles.
    """

    # Custom OID for roles in certificates
    ROLE_EXTENSION_OID = "1.3.6.1.4.1.99999.1"

    @staticmethod
    def validate_single_role(role: str) -> bool:
        """
        Validate a single role.

        Args:
            role: Role string to validate

        Returns:
            True if role is valid, False otherwise
        """
        if not isinstance(role, str):
            return False

        # Check if role is not empty after trimming
        if not role.strip():
            return False

        # Check for valid characters (alphanumeric, hyphens, underscores)
        valid_chars = set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        )
        role_chars = set(role.lower())

        if not role_chars.issubset(valid_chars):
            return False

        # Check length (1-50 characters)
        if len(role) < 1 or len(role) > 50:
            return False

        return True

    @staticmethod
    def normalize_role(role: str) -> str:
        """
        Normalize role string.

        Args:
            role: Role string to normalize

        Returns:
            Normalized role string
        """
        if not role:
            return ""

        # Convert to lowercase and trim whitespace
        normalized = role.lower().strip()

        # Replace multiple spaces with single space
        normalized = " ".join(normalized.split())

        # Replace spaces with hyphens
        normalized = normalized.replace(" ", "-")

        return normalized

    @staticmethod
    def normalize_roles(roles: List[str]) -> List[str]:
        """
        Normalize list of roles.

        Args:
            roles: List of roles to normalize

        Returns:
            List of normalized roles
        """
        if not roles:
            return []

        normalized = []
        for role in roles:
            normalized_role = RoleUtils.normalize_role(role)
            if normalized_role and normalized_role not in normalized:
                normalized.append(normalized_role)

        return normalized
