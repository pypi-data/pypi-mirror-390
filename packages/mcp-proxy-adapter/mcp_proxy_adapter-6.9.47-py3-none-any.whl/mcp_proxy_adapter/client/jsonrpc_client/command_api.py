"""Command helpers for JsonRpcClient.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from mcp_proxy_adapter.client.jsonrpc_client.transport import JsonRpcTransport


class CommandApiMixin(JsonRpcTransport):
    """Mixin providing standard JSON-RPC command helpers."""

    async def echo(
        self, message: str = "Hello, World!", timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"message": message}
        if timestamp:
            params["timestamp"] = timestamp
        response = await self.jsonrpc_call("echo", params)
        return self._extract_result(response)

    async def help(
        self, command_name: Optional[str] = None
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if command_name:
            params["command"] = command_name
        response = await self.jsonrpc_call("help", params)
        return self._extract_result(response)

    async def get_config(self) -> Dict[str, Any]:
        response = await self.jsonrpc_call("config", {})
        return self._extract_result(response)

    async def long_task(self, seconds: int) -> Dict[str, Any]:
        response = await self.jsonrpc_call("long_task", {"seconds": seconds})
        return self._extract_result(response)

    async def job_status(self, job_id: str) -> Dict[str, Any]:
        response = await self.jsonrpc_call("job_status", {"job_id": job_id})
        return self._extract_result(response)
