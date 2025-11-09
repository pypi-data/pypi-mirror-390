"""Async helper routines for proxy heartbeat and unregister flows.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from mcp_proxy_adapter.client.jsonrpc_client import JsonRpcClient

from .registration_context import HeartbeatSettings, ProxyCredentials


def create_heartbeat_task(
    proxy_url: str,
    server_name: str,
    server_url: str,
    capabilities: List[str],
    metadata: Dict[str, Any],
    settings: HeartbeatSettings,
    credentials: ProxyCredentials,
    logger: Any,
) -> asyncio.Task:
    """Create and return an asyncio Task that sends heartbeats."""

    interval = max(2, settings.interval)

    async def heartbeat_loop() -> None:
        client = JsonRpcClient(protocol="http", host="127.0.0.1", port=8080)
        try:

            async def _send() -> None:
                await client.heartbeat_to_proxy(
                    proxy_url=proxy_url,
                    server_name=server_name,
                    server_url=server_url,
                    capabilities=list(capabilities),
                    metadata=metadata,
                    cert=credentials.cert,
                    verify=credentials.verify,
                )

            while True:
                try:
                    await asyncio.sleep(interval)
                    await _send()
                    logger.debug("\ud83d\udc93 Heartbeat sent successfully")
                except asyncio.CancelledError:
                    raise
                except Exception as exc:  # noqa: BLE001
                    logger.error(f"Heartbeat error: {exc}")
        except asyncio.CancelledError:
            logger.debug("Heartbeat loop cancelled")
            raise
        finally:
            await client.close()

    return asyncio.create_task(heartbeat_loop())


async def unregister_from_proxy(
    proxy_url: str,
    server_name: str,
    endpoint: str,
    credentials: ProxyCredentials,
    logger: Any,
) -> None:
    """Unregister adapter from proxy using provided credentials."""

    client = JsonRpcClient(protocol="http", host="127.0.0.1", port=8080)
    try:
        full_url = f"{proxy_url}{endpoint}"
        await client.unregister_from_proxy(
            proxy_url=full_url,
            server_name=server_name,
            cert=credentials.cert,
            verify=credentials.verify,
        )
        logger.info(f"\ud83d\udd1a Unregistered from proxy: {server_name}")
    finally:
        await client.close()
