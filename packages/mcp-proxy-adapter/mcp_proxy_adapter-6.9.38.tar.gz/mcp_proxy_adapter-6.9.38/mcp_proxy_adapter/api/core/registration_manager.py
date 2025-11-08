"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Registration management utilities for MCP Proxy Adapter API.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from mcp_proxy_adapter.client.jsonrpc_client import JsonRpcClient
from mcp_proxy_adapter.core.logging import get_global_logger

from mcp_proxy_adapter.api.core.registration_context import (
    HeartbeatSettings,
    ProxyCredentials,
    RegistrationContext,
    prepare_registration_context,
    resolve_heartbeat_settings,
    resolve_runtime_credentials,
    resolve_unregister_endpoint,
)
from mcp_proxy_adapter.api.core.registration_tasks import (
    create_heartbeat_task,
    unregister_from_proxy as unregister_task,
)


class RegistrationManager:
    """Manager for proxy registration functionality using JsonRpcClient."""

    def __init__(self) -> None:
        """Initialize registration manager."""
        self.logger = get_global_logger()
        self.registered = False
        self.registration_task: Optional[asyncio.Task] = None
        self.server_name: Optional[str] = None
        self.server_url: Optional[str] = None
        self.proxy_url: Optional[str] = None
        self.capabilities: List[str] = []
        self.metadata: Dict[str, Any] = {}
        self.config: Optional[Dict[str, Any]] = None
        self._use_proxy_client = False
        self._proxy_client_config: Dict[str, Any] = {}
        self._proxy_registration_config: Dict[str, Any] = {}
        self._registration_credentials: Optional[ProxyCredentials] = None
        self._runtime_credentials: Optional[ProxyCredentials] = None
        self._register_endpoint: str = "/register"
        self._heartbeat_settings: Optional[HeartbeatSettings] = None

    async def register_with_proxy(self, config: Dict[str, Any]) -> bool:
        """
        Register this server with the proxy using JsonRpcClient.

        Supports both ``proxy_client`` (SimpleConfig format) and ``proxy_registration`` (legacy format).
        Registration is controlled by ``registration.auto_on_startup`` rather than ``proxy_client.enabled``.
        """

        context = prepare_registration_context(config, self.logger)
        if context is None:
            return True

        self._apply_context(context, config)

        proxy_url = self.proxy_url
        assert proxy_url is not None
        assert self.server_name is not None
        assert self.server_url is not None

        client = JsonRpcClient(protocol="http", host="127.0.0.1", port=8080)

        async def _register() -> Dict[str, Any]:
            self._log_credentials("🔐 Registration SSL config", context.credentials)
            self.logger.info(f"📡 Connecting to proxy: {proxy_url}")
            self.logger.debug(
                "   Endpoint: %s, Server: %s -> %s",
                self._register_endpoint,
                self.server_name,
                self.server_url,
            )
            return await client.register_with_proxy(
                proxy_url=proxy_url,
                server_name=context.server_name,
                server_url=context.advertised_url,
                capabilities=self.capabilities,
                metadata=self.metadata,
                cert=context.credentials.cert,
                verify=context.credentials.verify,
            )

        max_retries = 5
        retry_delay = 2

        try:
            for attempt in range(max_retries):
                try:
                    registration_response = await _register()
                    if registration_response is not None:
                        self.logger.debug(
                            "Proxy registration response payload: %s",
                            registration_response,
                        )
                    self.logger.info(
                        "✅ Successfully registered with proxy as %s -> %s",
                        self.server_name,
                        self.server_url,
                    )
                    self.registered = True
                    return True
                except Exception as exc:  # noqa: BLE001
                    full_error = self._format_httpx_error(exc)
                    if attempt < max_retries - 1:
                        self.logger.warning(
                            "⚠️  Registration attempt %s/%s failed: %s. Retrying in %ss...",
                            attempt + 1,
                            max_retries,
                            full_error,
                            retry_delay,
                        )
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        self.logger.error(
                            "❌ Failed to register with proxy after %s attempts: %s",
                            max_retries,
                            full_error,
                        )
                        return False
        except Exception as exc:  # noqa: BLE001
            self.logger.error(f"❌ Registration error: {exc}")
            return False
        finally:
            await client.close()

        return False

    async def start_heartbeat(self, _config: Dict[str, Any]) -> None:
        """Start heartbeat task using JsonRpcClient."""

        if not self._can_start_tasks() or not self.registered:
            return

        credentials = resolve_runtime_credentials(
            self._use_proxy_client,
            self._proxy_client_config,
            self._proxy_registration_config,
        )
        settings = resolve_heartbeat_settings(
            self._use_proxy_client,
            self._proxy_client_config,
            self._proxy_registration_config,
        )
        self._runtime_credentials = credentials
        self._heartbeat_settings = settings

        heartbeat_url = f"{self.proxy_url}{settings.endpoint}"
        self.logger.info(
            "💓 Starting heartbeat task (interval: %ss)", settings.interval
        )

        assert self.server_name is not None
        assert self.server_url is not None

        self.registration_task = create_heartbeat_task(
            proxy_url=heartbeat_url,
            server_name=self.server_name,
            server_url=self.server_url,
            capabilities=self.capabilities,
            metadata=self.metadata,
            settings=settings,
            credentials=credentials,
            logger=self.logger,
        )

    async def stop(self) -> None:
        """Stop registration manager and unregister from proxy."""

        if self.registration_task:
            self.registration_task.cancel()
            try:
                await self.registration_task
            except asyncio.CancelledError:
                pass
            self.registration_task = None

        if not (self.registered and self._can_start_tasks() and self.config):
            self.registered = False
            return

        credentials = self._runtime_credentials or resolve_runtime_credentials(
            self._use_proxy_client,
            self._proxy_client_config,
            self._proxy_registration_config,
        )
        endpoint = resolve_unregister_endpoint(
            self._use_proxy_client,
            self._proxy_client_config,
        )

        assert self.proxy_url is not None
        assert self.server_name is not None

        try:
            await unregister_task(
                proxy_url=self.proxy_url,
                server_name=self.server_name,
                endpoint=endpoint,
                credentials=credentials,
                logger=self.logger,
            )
        except Exception as exc:  # noqa: BLE001
            self.logger.error(f"Error unregistering from proxy: {exc}")
        finally:
            self.registered = False

    def _apply_context(
        self, context: RegistrationContext, config: Dict[str, Any]
    ) -> None:
        self.server_name = context.server_name
        self.server_url = context.advertised_url
        self.proxy_url = context.proxy_url
        self.capabilities = list(context.capabilities)
        self.metadata = dict(context.metadata)
        self.config = config
        self._use_proxy_client = context.use_proxy_client
        self._proxy_client_config = context.proxy_client_config
        self._proxy_registration_config = context.proxy_registration_config
        self._registration_credentials = context.credentials
        self._runtime_credentials = None
        self._register_endpoint = context.register_endpoint

    def _log_credentials(self, prefix: str, credentials: ProxyCredentials) -> None:
        self.logger.info(
            "%s: cert=%s, verify=%s",
            prefix,
            credentials.cert is not None,
            credentials.verify,
        )
        if credentials.cert:
            self.logger.debug("   Client cert: %s, key: %s", *credentials.cert)
        if isinstance(credentials.verify, str):
            self.logger.debug("   CA cert: %s", credentials.verify)

    def _format_httpx_error(self, exc: Exception) -> str:
        import httpx

        error_msg = str(exc) or type(exc).__name__
        details: List[str] = [f"type={type(exc).__name__}"]

        if isinstance(exc, httpx.HTTPStatusError):
            details.append(f"status={exc.response.status_code}")
            try:
                details.append(f"response={exc.response.text[:200]}")
            except Exception:  # noqa: BLE001
                pass
        elif isinstance(exc, httpx.ConnectError):
            details.append("connection_failed")
            if hasattr(exc, "request"):
                details.append(f"url={exc.request.url}")
        elif isinstance(exc, httpx.TimeoutException):
            details.append("timeout")

        return f"{error_msg} ({', '.join(details)})" if details else error_msg

    def _can_start_tasks(self) -> bool:
        return bool(self.proxy_url and self.server_name and self.server_url)
