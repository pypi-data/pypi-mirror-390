"""Transport utilities for asynchronous JSON-RPC client.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union, cast

import httpx


class JsonRpcTransport:
    """Base transport class providing HTTP primitives."""

    def __init__(
        self,
        protocol: str = "http",
        host: str = "127.0.0.1",
        port: int = 8080,
        token_header: Optional[str] = None,
        token: Optional[str] = None,
        cert: Optional[str] = None,
        key: Optional[str] = None,
        ca: Optional[str] = None,
    ) -> None:
        scheme = "https" if protocol in ("https", "mtls") else "http"
        self.base_url = f"{scheme}://{host}:{port}"

        self.headers: Dict[str, str] = {"Content-Type": "application/json"}
        if token_header and token:
            self.headers[token_header] = token

        self.verify: Union[bool, str] = True
        self.cert: Optional[Tuple[str, str]] = None

        if protocol in ("https", "mtls"):
            if cert and key:
                self.cert = (str(Path(cert)), str(Path(key)))
            if ca:
                self.verify = str(Path(ca))
            else:
                self.verify = False

        self.timeout = 30.0
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Return cached async HTTP client or create it lazily."""

        if self._client is None:
            self._client = httpx.AsyncClient(
                verify=self.verify,
                cert=self.cert,
                timeout=self.timeout,
            )
        return self._client

    async def close(self) -> None:
        """Close underlying HTTPX client."""

        if self._client:
            await self._client.aclose()
            self._client = None

    async def health(self) -> Dict[str, Any]:
        """Fetch health information from service."""

        client = await self._get_client()
        response = await client.get(f"{self.base_url}/health", headers=self.headers)
        response.raise_for_status()
        return cast(Dict[str, Any], response.json())

    async def jsonrpc_call(
        self,
        method: str,
        params: Dict[str, Any],
        req_id: int = 1,
    ) -> Dict[str, Any]:
        """Perform JSON-RPC request and return raw response payload."""

        payload: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": req_id,
        }
        client = await self._get_client()
        response = await client.post(
            f"{self.base_url}/api/jsonrpc",
            json=payload,
            headers=self.headers,
        )
        response.raise_for_status()
        return cast(Dict[str, Any], response.json())

    def _extract_result(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ``result`` part from JSON-RPC reply raising on error."""

        if "error" in response:
            error = response["error"]
            message = error.get("message", "Unknown error")
            code = error.get("code", -1)
            raise RuntimeError(f"JSON-RPC error: {message} (code: {code})")
        result_data = response.get("result", {})
        return cast(Dict[str, Any], result_data)
