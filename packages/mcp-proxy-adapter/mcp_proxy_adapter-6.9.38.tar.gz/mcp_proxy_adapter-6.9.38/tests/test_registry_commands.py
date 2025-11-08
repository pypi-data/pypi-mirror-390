#!/usr/bin/env python3
"""
Test script to check registry commands.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mcp_proxy_adapter'))

from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.commands.builtin_commands import register_builtin_commands

print("Testing registry commands...")

# Register built-in commands first
try:
    count = register_builtin_commands()
    print(f"✅ Registered {count} built-in commands")
except Exception as e:
    print(f"❌ Failed to register built-in commands: {e}")

# List all registered commands
print("\nBuilt-in commands:")
for name, command in registry._builtin_commands.items():
    print(f"  - {name}: {command.__class__.__name__}")

print(f"\nTotal built-in commands: {len(registry._builtin_commands)}")

# Test specific commands
test_commands = ["echo", "list", "help", "health"]
for cmd_name in test_commands:
    try:
        cmd = registry.get_command(cmd_name)
        if cmd:
            print(f"✅ {cmd_name}: {cmd.__class__.__name__}")
        else:
            print(f"❌ {cmd_name}: Not found")
    except Exception as e:
        print(f"❌ {cmd_name}: Error - {e}")

# Test registry methods
print(f"\nRegistry methods:")
print(f"  - get_command('echo'): {registry.get_command('echo')}")
print(f"  - has_command('echo'): {registry.has_command('echo')}")
print(f"  - list_commands(): {registry.list_commands()}")
