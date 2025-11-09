"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

SSL context manager for security testing.
"""

import os
import ssl
from pathlib import Path
from typing import Optional


class SSLContextManager:
    """Manager for SSL contexts in security testing."""

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize SSL context manager.

        Args:
            project_root: Root directory of the project (optional)
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent.parent
        self.project_root = project_root


