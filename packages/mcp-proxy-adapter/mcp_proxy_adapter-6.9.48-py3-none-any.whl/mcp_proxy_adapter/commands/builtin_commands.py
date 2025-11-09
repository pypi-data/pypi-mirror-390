"""
Module for registering built-in framework commands.

This module contains the procedure for adding predefined commands
that are part of the framework.
"""

from typing import List
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.commands.help_command import HelpCommand
from mcp_proxy_adapter.commands.health_command import HealthCommand
from mcp_proxy_adapter.commands.config_command import ConfigCommand
from mcp_proxy_adapter.commands.reload_command import ReloadCommand
from mcp_proxy_adapter.commands.settings_command import SettingsCommand
from mcp_proxy_adapter.commands.load_command import LoadCommand
from mcp_proxy_adapter.commands.unload_command import UnloadCommand
from mcp_proxy_adapter.commands.plugins_command import PluginsCommand
from mcp_proxy_adapter.commands.transport_management_command import (
    TransportManagementCommand,
)
from mcp_proxy_adapter.commands.proxy_registration_command import (
    ProxyRegistrationCommand,
)
from mcp_proxy_adapter.commands.echo_command import EchoCommand
from mcp_proxy_adapter.commands.role_test_command import RoleTestCommand
from mcp_proxy_adapter.core.logging import get_global_logger




