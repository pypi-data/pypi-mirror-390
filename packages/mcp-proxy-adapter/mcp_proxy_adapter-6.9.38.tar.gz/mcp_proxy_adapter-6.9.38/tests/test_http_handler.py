#!/usr/bin/env python3
"""
Test script to check HTTP handler.
"""
import sys
import os
import asyncio
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mcp_proxy_adapter'))

from mcp_proxy_adapter.api.handlers import jsonrpc_endpoint
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.commands.builtin_commands import register_builtin_commands

async def test_http_handler():
    print("Testing HTTP handler...")
    
    # Register built-in commands first
    try:
        count = register_builtin_commands()
        print(f"✅ Registered {count} built-in commands")
    except Exception as e:
        print(f"❌ Failed to register built-in commands: {e}")
        return
    
    # Test JSON-RPC request
    request_data = {
        "jsonrpc": "2.0",
        "method": "echo",
        "params": {"message": "Hello World"},
        "id": 1
    }
    
    try:
        # Simulate HTTP request
        from fastapi import Request
        from fastapi.testclient import TestClient
        
        # Create a mock request
        request = Request({"type": "http", "method": "POST", "url": "/api/jsonrpc"})
        
        # Call the JSON-RPC endpoint
        response = await jsonrpc_endpoint(request_data, request)
        print(f"✅ JSON-RPC response: {response}")
        
    except Exception as e:
        print(f"❌ JSON-RPC handler failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_http_handler())
