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
    registration_manager: Any,
    proxy_url: str,
    server_name: str,
    server_url: str,
    capabilities: List[str],
    metadata: Dict[str, Any],
    settings: HeartbeatSettings,
    credentials: ProxyCredentials,
    logger: Any,
) -> asyncio.Task:
    """Create and return an asyncio Task that sends heartbeats.

    The heartbeat loop will:
    1. Check global registration status (with mutex)
    2. If not registered, attempt registration
    3. If registered, send heartbeat
    """

    interval = max(2, settings.interval)

    # Import here to avoid circular import
    from mcp_proxy_adapter.api.core.registration_manager import (
        get_registration_status,
        set_registration_status,
    )

    async def heartbeat_loop() -> None:
        client = JsonRpcClient(protocol="http", host="127.0.0.1", port=8080)
        try:
            while True:
                try:
                    # Check registration status (thread-safe with mutex)
                    is_registered = await get_registration_status()

                    if not is_registered:
                        # Attempt registration
                        if registration_manager._registration_config:
                            logger.info(
                                "📡 Attempting registration via heartbeat loop..."
                            )
                            success = await registration_manager.register_with_proxy(
                                registration_manager._registration_config
                            )
                            if success:
                                await set_registration_status(True)
                                logger.info(
                                    "✅ Registration successful via heartbeat loop"
                                )
                            else:
                                logger.warning(
                                    "⚠️  Registration failed, will retry on next heartbeat"
                                )
                        # Wait shorter interval before retry
                        await asyncio.sleep(min(5, interval))
                    else:
                        # Send heartbeat
                        await client.heartbeat_to_proxy(
                            proxy_url=proxy_url,
                            server_name=server_name,
                            server_url=server_url,
                            capabilities=list(capabilities),
                            metadata=metadata,
                            cert=credentials.cert,
                            verify=credentials.verify,
                        )
                        logger.debug("💓 Heartbeat sent successfully")
                        await asyncio.sleep(interval)
                except asyncio.CancelledError:
                    raise
                except Exception as exc:  # noqa: BLE001
                    logger.error(f"Heartbeat/Registration error: {exc}")
                    await asyncio.sleep(interval)
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
