"""Queue management helpers for JsonRpcClient.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from mcp_proxy_adapter.client.jsonrpc_client.transport import JsonRpcTransport


class QueueApiMixin(JsonRpcTransport):
    """Mixin with queue-related JSON-RPC shortcuts."""

    async def queue_health(self) -> Dict[str, Any]:
        response = await self.jsonrpc_call("queue_health", {})
        return self._extract_result(response)

    async def queue_add_job(
        self,
        job_type: str,
        job_id: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        payload = {"job_type": job_type, "job_id": job_id, "params": params}
        response = await self.jsonrpc_call("queue_add_job", payload)
        return self._extract_result(response)

    async def queue_start_job(self, job_id: str) -> Dict[str, Any]:
        response = await self.jsonrpc_call("queue_start_job", {"job_id": job_id})
        return self._extract_result(response)

    async def queue_stop_job(self, job_id: str) -> Dict[str, Any]:
        response = await self.jsonrpc_call("queue_stop_job", {"job_id": job_id})
        return self._extract_result(response)

    async def queue_delete_job(self, job_id: str) -> Dict[str, Any]:
        response = await self.jsonrpc_call("queue_delete_job", {"job_id": job_id})
        return self._extract_result(response)

    async def queue_get_job_status(self, job_id: str) -> Dict[str, Any]:
        response = await self.jsonrpc_call(
            "queue_get_job_status", {"job_id": job_id}
        )
        return self._extract_result(response)

    async def queue_list_jobs(
        self,
        status: Optional[str] = None,
        job_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if status:
            params["status"] = status
        if job_type:
            params["job_type"] = job_type
        response = await self.jsonrpc_call("queue_list_jobs", params)
        return self._extract_result(response)
