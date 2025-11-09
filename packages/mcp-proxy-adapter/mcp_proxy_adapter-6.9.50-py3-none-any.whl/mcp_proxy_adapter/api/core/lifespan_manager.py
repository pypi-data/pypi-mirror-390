"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Lifespan management utilities for MCP Proxy Adapter API.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from fastapi import FastAPI

from mcp_proxy_adapter.core.logging import get_global_logger
from .registration_manager import RegistrationManager


class LifespanManager:
    """Manager for application lifespan events."""

    def __init__(self):
        """Initialize lifespan manager."""
        self.logger = get_global_logger()
        self.registration_manager = RegistrationManager()

    def create_lifespan(self, config_path: Optional[str] = None, current_config: Optional[Dict[str, Any]] = None):
        """
        Create lifespan manager for the FastAPI application.

        Args:
            config_path: Path to configuration file (optional)
            current_config: Current configuration data (optional)

        Returns:
            Lifespan context manager
        """

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """Lifespan context manager."""
            # Startup
            get_global_logger().info("Starting MCP Proxy Adapter")
            
            # Register with proxy if configured
            if current_config:
                await self.registration_manager.register_with_proxy(current_config)
                await self.registration_manager.start_heartbeat(current_config)
            
            yield
            
            # Shutdown
            get_global_logger().info("Shutting down MCP Proxy Adapter")
            await self.registration_manager.stop()

        return lifespan
