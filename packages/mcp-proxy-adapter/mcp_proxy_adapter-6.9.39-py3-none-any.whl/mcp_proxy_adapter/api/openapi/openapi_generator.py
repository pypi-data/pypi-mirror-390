"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Main OpenAPI generator for MCP Proxy Adapter.
"""

from copy import deepcopy
from typing import Any, Dict, Optional

from fastapi import FastAPI

from mcp_proxy_adapter.core.logging import get_global_logger
from .schema_loader import SchemaLoader
from .command_integration import CommandIntegrator


class CustomOpenAPIGenerator:
    """
    Custom OpenAPI schema generator for compatibility with MCP-Proxy.

    EN:
    This generator creates an OpenAPI schema that matches the format expected by MCP-Proxy,
    enabling dynamic command loading and proper tool representation in AI models.
    Allows overriding title, description, and version for schema customization.

    RU:
    Кастомный генератор схемы OpenAPI для совместимости с MCP-Proxy.
    Позволяет создавать схему OpenAPI в формате, ожидаемом MCP-Proxy,
    с возможностью динамической подгрузки команд и корректного отображения инструментов для AI-моделей.
    Поддерживает переопределение title, description и version для кастомизации схемы.
    """

    def __init__(self):
        """Initialize the generator."""
        self.logger = get_global_logger()
        self.schema_loader = SchemaLoader()
        self.command_integrator = CommandIntegrator()
        self.base_schema = self.schema_loader.load_base_schema()

