"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Validation result classes for MCP Proxy Adapter configuration validation.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class ValidationLevel(Enum):
    """Validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Result of configuration validation."""
    level: str  # "error", "warning", "info"
    message: str
    section: Optional[str] = None
    key: Optional[str] = None
    suggestion: Optional[str] = None
