#!/usr/bin/env python3
"""
Test script to check command registration.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mcp_proxy_adapter'))

from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.commands.builtin_commands import register_builtin_commands

print("Testing command registration...")

# Register built-in commands
try:
    count = register_builtin_commands()
    print(f"✅ Registered {count} built-in commands")
except Exception as e:
    print(f"❌ Failed to register built-in commands: {e}")

# List all registered commands
print("\nRegistered commands:")
for name, command in registry._builtin_commands.items():
    print(f"  - {name}: {command.__class__.__name__}")

print(f"\nTotal commands: {len(registry._builtin_commands)}")

# Test echo command
try:
    echo_cmd = registry.get_command("echo")
    if echo_cmd:
        print(f"✅ Echo command found: {echo_cmd.__class__.__name__}")
    else:
        print("❌ Echo command not found")
except Exception as e:
    print(f"❌ Error getting echo command: {e}")
