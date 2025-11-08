"""Facade JsonRpcClient combining transport and feature mixins.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from __future__ import annotations

from typing import Optional

from mcp_proxy_adapter.client.jsonrpc_client.command_api import CommandApiMixin
from mcp_proxy_adapter.client.jsonrpc_client.proxy_api import ProxyApiMixin
from mcp_proxy_adapter.client.jsonrpc_client.queue_api import QueueApiMixin


class JsonRpcClient(ProxyApiMixin, QueueApiMixin, CommandApiMixin):
    """High-level asynchronous JSON-RPC client facade."""

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
        super().__init__(
            protocol=protocol,
            host=host,
            port=port,
            token_header=token_header,
            token=token,
            cert=cert,
            key=key,
            ca=ca,
        )


__all__ = ["JsonRpcClient"]
