"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

HTTP handlers for the MCP Proxy Adapter API.
Provides JSON-RPC handling and health/commands endpoints.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional

from fastapi import Request

from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.core.errors import (
    MicroserviceError,
    NotFoundError,
    InvalidRequestError,
    MethodNotFoundError,
    InvalidParamsError,
    InternalError,
)
from mcp_proxy_adapter.core.logging import get_global_logger, RequestLogger


async def execute_command(
    command_name: str,
    params: Dict[str, Any],
    request_id: Optional[str] = None,
    request: Optional[Request] = None,
) -> Dict[str, Any]:
    """Execute a registered command by name with parameters.

    Raises MethodNotFoundError if command is not found.
    Wraps unexpected exceptions into InternalError.
    """
    logger = RequestLogger(__name__, request_id) if request_id else get_global_logger()

    try:
        logger.info(f"Executing command: {command_name}")

        # Resolve command
        try:
            command_class = registry.get_command(command_name)
        except Exception:
            raise MethodNotFoundError(f"Method not found: {command_name}")

        # Build context (user info if middleware set state)
        context: Dict[str, Any] = {}
        if request is not None and hasattr(request, "state"):
            user_id = getattr(request.state, "user_id", None)
            user_role = getattr(request.state, "user_role", None)
            user_roles = getattr(request.state, "user_roles", None)
            if user_id or user_role or user_roles:
                context["user"] = {
                    "id": user_id,
                    "role": user_role,
                    "roles": user_roles or [],
                }

        # Execute with timeout
        started_at = time.time()
        try:
            result_obj = await asyncio.wait_for(
                command_class.run(**params, context=context), timeout=30.0
            )
        except asyncio.TimeoutError:
            elapsed = time.time() - started_at
            raise InternalError(f"Command timed out after {elapsed:.2f}s")

        elapsed = time.time() - started_at
        logger.info(f"Command '{command_name}' executed in {elapsed:.3f}s")
        return result_obj.to_dict()

    except MicroserviceError:
        raise
    except Exception as exc:
        logger.exception(f"Unhandled error in command '{command_name}': {exc}")
        raise InternalError("Internal error", data={"error": str(exc)})


async def handle_batch_json_rpc(
    batch_requests: List[Dict[str, Any]], request: Optional[Request] = None
) -> List[Dict[str, Any]]:
    """Handle batch JSON-RPC requests."""
    responses: List[Dict[str, Any]] = []
    request_id = getattr(request.state, "request_id", None) if request else None
    for item in batch_requests:
        responses.append(await handle_json_rpc(item, request_id, request))
    return responses


async def handle_json_rpc(
    request_data: Dict[str, Any],
    request_id: Optional[str] = None,
    request: Optional[Request] = None,
) -> Dict[str, Any]:
    """Handle a single JSON-RPC request with strict 2.0 compatibility.

    Also supports simplified form: {"command": "echo", "params": {...}}.
    """
    logger = RequestLogger(__name__, request_id) if request_id else get_global_logger()

    method: Optional[str]
    params: Dict[str, Any]
    json_rpc_id: Any

    if "jsonrpc" in request_data:
        if request_data.get("jsonrpc") != "2.0":
            return _error_response(InvalidRequestError("Invalid Request: jsonrpc must be '2.0'"), request_data.get("id"))
        method = request_data.get("method")
        params = request_data.get("params", {})
        json_rpc_id = request_data.get("id")
        if not method:
            return _error_response(InvalidRequestError("Invalid Request: method is required"), json_rpc_id)
    else:
        # Simplified
        method = request_data.get("command")
        params = request_data.get("params", {})
        json_rpc_id = request_data.get("id", 1)
        if not method:
            return _error_response(InvalidRequestError("Invalid Request: command is required"), json_rpc_id)

    try:
        result = await execute_command(method, params, request_id, request)
        return {"jsonrpc": "2.0", "result": result, "id": json_rpc_id}
    except MicroserviceError as err:
        return _error_response(err, json_rpc_id)
    except Exception as exc:
        logger.exception(f"Unhandled error in JSON-RPC handler: {exc}")
        return _error_response(InternalError("Internal error", data={"error": str(exc)}), json_rpc_id)


def _error_response(error: MicroserviceError, request_id: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "error": error.to_dict(), "id": request_id}


async def get_server_health() -> Dict[str, Any]:
    """Return server health info."""
    import os
    import platform
    import sys
    import psutil
    from datetime import datetime

    process = psutil.Process(os.getpid())
    start_time = datetime.fromtimestamp(process.create_time())
    uptime_seconds = (datetime.now() - start_time).total_seconds()
    mem = process.memory_info().rss / (1024 * 1024)

    return {
        "status": "ok",
        "model": "mcp-proxy-adapter",
        "version": "1.0.0",
        "uptime": uptime_seconds,
        "components": {
            "system": {
                "python_version": sys.version,
                "platform": platform.platform(),
                "cpu_count": os.cpu_count(),
            },
            "process": {
                "pid": os.getpid(),
                "memory_usage_mb": mem,
                "start_time": start_time.isoformat(),
            },
            "commands": {"registered_count": len(registry.get_all_commands())},
        },
    }


async def get_commands_list() -> Dict[str, Dict[str, Any]]:
    """Return list of registered commands with schemas."""
    result: Dict[str, Dict[str, Any]] = {}
    for name, cls in registry.get_all_commands().items():
        schema = cls.get_schema()
        result[name] = {"name": name, "schema": schema, "description": schema.get("description", "")}
    return result
