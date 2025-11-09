"""
Integration modules for mcp_proxy_adapter.

This package contains integrations with external systems and libraries
to extend the functionality of the MCP Proxy Adapter framework.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from .queuemgr_integration import (
    QueueManagerIntegration,
    QueueJobBase,
    QueueJobResult,
    QueueJobStatus,
    QueueJobError,
)

__all__ = [
    "QueueManagerIntegration",
    "QueueJobBase", 
    "QueueJobResult",
    "QueueJobStatus",
    "QueueJobError",
]
