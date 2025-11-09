"""
Module for command registration hooks.

This module provides a hook system for registering custom commands
that will be called during system initialization.
"""

from enum import Enum
from dataclasses import dataclass
from mcp_proxy_adapter.core.logging import get_global_logger


class HookType(Enum):
    """Types of hooks that can be registered."""

    CUSTOM_COMMANDS = "custom_commands"
    BEFORE_INIT = "before_init"
    AFTER_INIT = "after_init"
    BEFORE_COMMAND = "before_command"
    AFTER_COMMAND = "after_command"
    BEFORE_EXECUTION = "before_execution"
    AFTER_EXECUTION = "after_execution"


@dataclass
class HookContext:
    """Context object passed to hook functions."""

    hook_type: HookType
    command_name: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    registry: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None
    standard_processing: bool = True

    def __post_init__(self):
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}


class CommandHooks:
    """
    Hook system for command registration.
    """

    def __init__(self):
        """
        Initialize command hooks.
        """
        self._custom_commands_hooks: List[Callable] = []
        self._before_init_hooks: List[Callable] = []
        self._after_init_hooks: List[Callable] = []
        self._before_command_hooks: List[Callable] = []
        self._after_command_hooks: List[Callable] = []

    def register_custom_commands_hook(self, hook_func: Callable) -> None:
        """
        Register a hook function for custom commands registration.

        Args:
            hook_func: Function that registers custom commands.
                      Should accept registry as parameter.
        """
        self._custom_commands_hooks.append(hook_func)
        get_global_logger().debug(f"Registered custom commands hook: {hook_func.__name__}")

    def register_before_init_hook(self, hook_func: Callable) -> None:
        """
        Register a hook function to be called before system initialization.

        Args:
            hook_func: Function to call before initialization.
        """
        self._before_init_hooks.append(hook_func)
        get_global_logger().debug(f"Registered before init hook: {hook_func.__name__}")

    def register_after_init_hook(self, hook_func: Callable) -> None:
        """
        Register a hook function to be called after system initialization.

        Args:
            hook_func: Function to call after initialization.
        """
        self._after_init_hooks.append(hook_func)
        get_global_logger().debug(f"Registered after init hook: {hook_func.__name__}")

    def register_before_command_hook(self, hook_func: Callable) -> None:
        """
        Register a hook function to be called before command execution.

        Args:
            hook_func: Function to call before command execution.
                      Should accept command_name and params as parameters.
        """
        self._before_command_hooks.append(hook_func)
        get_global_logger().debug(f"Registered before command hook: {hook_func.__name__}")

    def register_after_command_hook(self, hook_func: Callable) -> None:
        """
        Register a hook function to be called after command execution.

        Args:
            hook_func: Function to call after command execution.
                      Should accept command_name, params, and result as parameters.
        """
        self._after_command_hooks.append(hook_func)
        get_global_logger().debug(f"Registered after command hook: {hook_func.__name__}")








# Global hooks instance
hooks = CommandHooks()


def register_custom_commands_hook(hook_func: Callable) -> None:
    """
    Register a hook function for custom commands registration.

    Args:
        hook_func: Function that registers custom commands.
                  Should accept registry as parameter.
    """
    hooks.register_custom_commands_hook(hook_func)


def register_before_init_hook(hook_func: Callable) -> None:
    """
    Register a hook function to be called before system initialization.

    Args:
        hook_func: Function to call before initialization.
    """
    hooks.register_before_init_hook(hook_func)


def register_after_init_hook(hook_func: Callable) -> None:
    """
    Register a hook function to be called after system initialization.

    Args:
        hook_func: Function to call after initialization.
    """
    hooks.register_after_init_hook(hook_func)


def register_before_command_hook(hook_func: Callable) -> None:
    """
    Register a hook function to be called before command execution.

    Args:
        hook_func: Function to call before command execution.
                  Should accept command_name and params as parameters.
    """
    hooks.register_before_command_hook(hook_func)


def register_after_command_hook(hook_func: Callable) -> None:
    """
    Register a hook function to be called after command execution.

    Args:
        hook_func: Function to call after command execution.
                  Should accept command_name, params, and result as parameters.
    """
    hooks.register_after_command_hook(hook_func)
