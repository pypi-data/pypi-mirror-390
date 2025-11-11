"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Proxy server commands for registration, heartbeat, and discovery.
These commands are used by the proxy server built on the adapter.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult, ErrorResult


# In-memory registry for proxy server
_registry: Dict[str, Dict[str, Dict[str, Any]]] = {}


class ProxyRegisterResult(SuccessResult):
    """Result of proxy register command."""

    def __init__(self, server_id: str, server_url: str, registered: bool):
        """Initialize proxy register result."""
        data = {
            "server_id": server_id,
            "server_url": server_url,
            "registered": registered,
        }
        super().__init__(data=data)

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for result."""
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "const": True},
                "data": {
                    "type": "object",
                    "properties": {
                        "server_id": {"type": "string"},
                        "server_url": {"type": "string"},
                        "registered": {"type": "boolean"},
                    },
                    "required": ["server_id", "server_url", "registered"],
                },
            },
            "required": ["success", "data"],
        }
    
    @property
    def server_id(self) -> str:
        """Get server ID."""
        return self.data.get("server_id", "")
    
    @property
    def server_url(self) -> str:
        """Get server URL."""
        return self.data.get("server_url", "")
    
    @property
    def registered(self) -> bool:
        """Get registered status."""
        return self.data.get("registered", False)


class ProxyUnregisterResult(SuccessResult):
    """Result of proxy unregister command."""

    def __init__(self, server_id: str, unregistered: bool):
        """Initialize proxy unregister result."""
        data = {
            "server_id": server_id,
            "unregistered": unregistered,
        }
        super().__init__(data=data)

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for result."""
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "const": True},
                "data": {
                    "type": "object",
                    "properties": {
                        "server_id": {"type": "string"},
                        "unregistered": {"type": "boolean"},
                    },
                    "required": ["server_id", "unregistered"],
                },
            },
            "required": ["success", "data"],
        }
    
    @property
    def server_id(self) -> str:
        """Get server ID."""
        return self.data.get("server_id", "")
    
    @property
    def unregistered(self) -> bool:
        """Get unregistered status."""
        return self.data.get("unregistered", False)


class ProxyHeartbeatResult(SuccessResult):
    """Result of proxy heartbeat command."""

    def __init__(self, server_id: str, heartbeat_received: bool):
        """Initialize proxy heartbeat result."""
        data = {
            "server_id": server_id,
            "heartbeat_received": heartbeat_received,
        }
        super().__init__(data=data)

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for result."""
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "const": True},
                "data": {
                    "type": "object",
                    "properties": {
                        "server_id": {"type": "string"},
                        "heartbeat_received": {"type": "boolean"},
                    },
                    "required": ["server_id", "heartbeat_received"],
                },
            },
            "required": ["success", "data"],
        }
    
    @property
    def server_id(self) -> str:
        """Get server ID."""
        return self.data.get("server_id", "")
    
    @property
    def heartbeat_received(self) -> bool:
        """Get heartbeat received status."""
        return self.data.get("heartbeat_received", False)


class ProxyListResult(SuccessResult):
    """Result of proxy list command."""

    def __init__(self, servers: List[Dict[str, Any]]):
        """Initialize proxy list result."""
        data = {"servers": servers}
        super().__init__(data=data)

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for result."""
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "const": True},
                "data": {
                    "type": "object",
                    "properties": {
                        "servers": {
                            "type": "array",
                            "items": {"type": "object"},
                        },
                    },
                    "required": ["servers"],
                },
            },
            "required": ["success", "data"],
        }
    
    @property
    def servers(self) -> List[Dict[str, Any]]:
        """Get servers list."""
        return self.data.get("servers", [])


class ProxyRegisterCommand(Command):
    """Register a server with the proxy."""

    async def execute(self, params: Dict[str, Any] = None, **kwargs) -> ProxyRegisterResult:
        """Execute proxy register command."""
        if params is None:
            params = kwargs
        server_id = params.get("server_id") or params.get("name", "")
        server_url = params.get("server_url") or params.get("url", "")
        capabilities = params.get("capabilities", [])
        metadata = params.get("metadata", {})

        if not server_id or not server_url:
            return ErrorResult(
                message="server_id (or name) and server_url (or url) are required",
                code=-32602,  # Invalid params
            )

        # Register server
        if server_id not in _registry:
            _registry[server_id] = {}

        # Simple registration (no server_key for now)
        _registry[server_id]["default"] = {
            "server_id": server_id,
            "server_url": server_url,
            "capabilities": capabilities,
            "metadata": metadata,
            "registered_at": time.time(),
            "last_heartbeat": time.time(),
        }

        return ProxyRegisterResult(
            server_id=server_id,
            server_url=server_url,
            registered=True,
        )


class ProxyUnregisterCommand(Command):
    """Unregister a server from the proxy."""

    async def execute(self, params: Dict[str, Any] = None, **kwargs) -> ProxyUnregisterResult:
        """Execute proxy unregister command."""
        if params is None:
            params = kwargs
        server_id = params.get("server_id") or params.get("name", "")

        if not server_id:
            return ErrorResult(
                message="server_id (or name) is required",
                code=-32602,  # Invalid params
            )

        unregistered = False
        if server_id in _registry:
            _registry.pop(server_id, None)
            unregistered = True

        return ProxyUnregisterResult(
            server_id=server_id,
            unregistered=unregistered,
        )


class ProxyHeartbeatCommand(Command):
    """Update server heartbeat."""

    async def execute(self, params: Dict[str, Any] = None, **kwargs) -> ProxyHeartbeatResult:
        """Execute proxy heartbeat command."""
        if params is None:
            params = kwargs
        server_id = params.get("server_id") or params.get("name", "")

        if not server_id:
            return ErrorResult(
                message="server_id (or name) is required",
                code=-32602,  # Invalid params
            )

        heartbeat_received = False
        if server_id in _registry and "default" in _registry[server_id]:
            _registry[server_id]["default"]["last_heartbeat"] = time.time()
            heartbeat_received = True

        return ProxyHeartbeatResult(
            server_id=server_id,
            heartbeat_received=heartbeat_received,
        )


class ProxyListCommand(Command):
    """List all registered servers."""

    async def execute(self, params: Dict[str, Any] = None, **kwargs) -> ProxyListResult:
        """Execute proxy list command."""
        if params is None:
            params = kwargs
        servers = []
        for server_id, instances in _registry.items():
            for instance_key, server_data in instances.items():
                servers.append(
                    {
                        "server_id": server_data.get("server_id", server_id),
                        "server_url": server_data.get("server_url", ""),
                        "capabilities": server_data.get("capabilities", []),
                        "metadata": server_data.get("metadata", {}),
                        "registered_at": server_data.get("registered_at", 0),
                        "last_heartbeat": server_data.get("last_heartbeat", 0),
                    }
                )

        return ProxyListResult(servers=servers)

