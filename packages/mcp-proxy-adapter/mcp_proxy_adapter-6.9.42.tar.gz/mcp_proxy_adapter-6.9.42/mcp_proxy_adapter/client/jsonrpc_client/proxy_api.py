"""Proxy registration helpers for JsonRpcClient.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import httpx

from mcp_proxy_adapter.client.jsonrpc_client.transport import JsonRpcTransport


class ProxyApiMixin(JsonRpcTransport):
    """Mixin providing proxy registration helpers."""

    async def register_with_proxy(
        self,
        proxy_url: str,
        server_name: str,
        server_url: str,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        cert: Optional[Tuple[str, str]] = None,
        verify: Optional[Union[bool, str]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "server_id": server_name,
            "server_url": server_url,
            "capabilities": capabilities or [],
            "metadata": metadata or {},
        }

        ssl_verify = verify if verify is not None else self.verify
        ssl_cert = cert if cert is not None else self.cert

        proxy_base = proxy_url.rstrip("/")
        register_url = (
            proxy_base if proxy_base.endswith("/register") else f"{proxy_base}/register"
        )

        logger = logging.getLogger(__name__)
        logger.debug(
            "Registering with proxy: %s, cert=%s, verify=%s",
            register_url,
            ssl_cert is not None,
            ssl_verify,
        )

        try:
            async with httpx.AsyncClient(
                verify=ssl_verify, cert=ssl_cert, timeout=10.0
            ) as client:
                response = await client.post(register_url, json=payload)

                if response.status_code == 400:
                    error_data = cast(Dict[str, Any], response.json())
                    error_msg = error_data.get("error", "").lower()
                    if "already registered" in error_msg:
                        await self._retry_registration_after_unregister(
                            client,
                            proxy_base,
                            register_url,
                            server_name,
                            server_url,
                            capabilities,
                            metadata,
                            error_data,
                        )

                if response.status_code >= 400:
                    try:
                        error_data = cast(Dict[str, Any], response.json())
                        error_msg = error_data.get(
                            "error",
                            error_data.get("message", f"HTTP {response.status_code}"),
                        )
                        raise httpx.HTTPStatusError(
                            f"Registration failed: {error_msg}",
                            request=response.request,
                            response=response,
                        )
                    except (ValueError, KeyError):
                        response.raise_for_status()

                response.raise_for_status()
                return cast(Dict[str, Any], response.json())
        except httpx.ConnectError as exc:  # noqa: BLE001
            error_msg = f"Connection failed to {register_url}"
            if hasattr(exc, "request"):
                error_msg += f" (request: {exc.request.url})"
            raise ConnectionError(error_msg) from exc
        except httpx.TimeoutException as exc:  # noqa: BLE001
            raise TimeoutError(f"Request timeout to {register_url}") from exc
        except httpx.HTTPError as exc:  # noqa: BLE001
            raise ConnectionError(
                f"HTTP error connecting to {register_url}: {exc}"
            ) from exc

    async def unregister_from_proxy(
        self,
        proxy_url: str,
        server_name: str,
        cert: Optional[Tuple[str, str]] = None,
        verify: Optional[Union[bool, str]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "server_id": server_name,
            "server_url": "",
            "capabilities": [],
            "metadata": {},
        }

        ssl_verify = verify if verify is not None else self.verify
        ssl_cert = cert if cert is not None else self.cert

        proxy_base = proxy_url.rstrip("/")
        unregister_url = (
            proxy_base
            if proxy_base.endswith("/unregister")
            else f"{proxy_base}/unregister"
        )

        async with httpx.AsyncClient(
            verify=ssl_verify, cert=ssl_cert, timeout=10.0
        ) as client:
            response = await client.post(unregister_url, json=payload)
            response.raise_for_status()
            return cast(Dict[str, Any], response.json())

    async def heartbeat_to_proxy(
        self,
        proxy_url: str,
        server_name: str,
        server_url: str,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        cert: Optional[Tuple[str, str]] = None,
        verify: Optional[Union[bool, str]] = None,
    ) -> None:
        payload: Dict[str, Any] = {
            "server_id": server_name,
            "server_url": server_url,
            "capabilities": capabilities or [],
            "metadata": metadata or {},
        }

        ssl_verify = verify if verify is not None else self.verify
        ssl_cert = cert if cert is not None else self.cert

        proxy_base = proxy_url.rstrip("/")
        async with httpx.AsyncClient(
            verify=ssl_verify, cert=ssl_cert, timeout=10.0
        ) as client:
            response = await client.post(
                f"{proxy_base}/proxy/heartbeat",
                json=payload,
            )
            response.raise_for_status()

    async def list_proxy_servers(self, proxy_url: str) -> Dict[str, Any]:
        proxy_base = proxy_url.rstrip("/")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{proxy_base}/proxy/list")
            response.raise_for_status()
            return cast(Dict[str, Any], response.json())

    async def get_proxy_health(self, proxy_url: str) -> Dict[str, Any]:
        proxy_base = proxy_url.rstrip("/")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{proxy_base}/proxy/health")
            response.raise_for_status()
            return cast(Dict[str, Any], response.json())

    async def _retry_registration_after_unregister(
        self,
        client: httpx.AsyncClient,
        proxy_base: str,
        register_url: str,
        server_name: str,
        server_url: str,
        capabilities: Optional[List[str]],
        metadata: Optional[Dict[str, Any]],
        error_data: Dict[str, Any],
    ) -> None:
        match = re.search(
            r"already registered as ([^\s,]+)",
            error_data.get("error", ""),
            re.IGNORECASE,
        )
        if not match:
            return

        registered_server_key = match.group(1)
        original_server_id = (
            re.sub(r"_\d+$", "", registered_server_key)
            if "_" in registered_server_key
            else registered_server_key
        )

        unregister_payload: Dict[str, Any] = {
            "server_id": original_server_id,
            "server_url": "",
            "capabilities": [],
            "metadata": {},
        }
        unregister_response = await client.post(
            f"{proxy_base}/unregister",
            json=unregister_payload,
        )
        if unregister_response.status_code != 200:
            return

        retry_payload: Dict[str, Any] = {
            "server_id": server_name,
            "server_url": server_url,
            "capabilities": capabilities or [],
            "metadata": metadata or {},
        }
        await client.post(register_url, json=retry_payload)
