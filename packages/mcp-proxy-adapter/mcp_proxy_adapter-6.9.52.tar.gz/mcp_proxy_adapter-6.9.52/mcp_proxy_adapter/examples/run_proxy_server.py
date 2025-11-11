#!/usr/bin/env python3
"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Proxy server built on MCP Proxy Adapter framework.
This server provides proxy registration endpoints via JSON-RPC commands.
"""

import argparse
import asyncio
import json
import signal
import sys
from pathlib import Path

from mcp_proxy_adapter.api.app import create_app
from mcp_proxy_adapter.core.server_engine import ServerEngineFactory
from mcp_proxy_adapter.commands.command_registry import registry

# Register proxy commands
from mcp_proxy_adapter.examples.full_application.proxy_commands import (
    ProxyRegisterCommand,
    ProxyUnregisterCommand,
    ProxyHeartbeatCommand,
    ProxyListCommand,
)


def register_proxy_commands():
    """Register proxy-specific commands."""
    registry._commands["proxy_register"] = ProxyRegisterCommand
    registry._command_types["proxy_register"] = "builtin"
    registry._commands["proxy_unregister"] = ProxyUnregisterCommand
    registry._command_types["proxy_unregister"] = "builtin"
    registry._commands["proxy_heartbeat"] = ProxyHeartbeatCommand
    registry._command_types["proxy_heartbeat"] = "builtin"
    registry._commands["proxy_list"] = ProxyListCommand
    registry._command_types["proxy_list"] = "builtin"


def main() -> None:
    """Main entry point for proxy server."""
    parser = argparse.ArgumentParser(
        description="Run proxy server built on MCP Proxy Adapter"
    )
    parser.add_argument(
        "--config",
        default="mcp_proxy_adapter/examples/full_application/configs/proxy_server.json",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=3004, help="Port to bind to (default: 3004)"
    )

    args = parser.parse_args()

    # Load configuration
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)

    try:
        with config_path.open("r", encoding="utf-8") as f:
            app_config = json.load(f)
    except Exception as exc:
        print(f"❌ Failed to load configuration: {exc}")
        sys.exit(1)

    # Override host and port from command line
    if args.host:
        app_config.setdefault("server", {}).update({"host": args.host})
    if args.port:
        app_config.setdefault("server", {}).update({"port": args.port})

    # Register proxy commands
    register_proxy_commands()

    # Create app using adapter
    app = create_app(
        title="MCP Proxy Server",
        description="Proxy server built on MCP Proxy Adapter",
        version="1.0.0",
        app_config=app_config,
        config_path=str(config_path),
    )

    # Add compatibility REST endpoints for backward compatibility
    from fastapi import APIRouter
    from fastapi.responses import JSONResponse
    from mcp_proxy_adapter.commands.result import SuccessResult, ErrorResult
    from mcp_proxy_adapter.examples.full_application.proxy_commands import _registry

    compatibility_router = APIRouter()

    @compatibility_router.post("/register")
    async def register_rest(request: dict):  # type: ignore[name-defined]
        """REST endpoint for registration (backward compatibility)."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"🔍 [PROXY] Received registration request: {request}")
        
        from mcp_proxy_adapter.examples.full_application.proxy_commands import (
            ProxyRegisterCommand,
        )

        try:
            cmd = ProxyRegisterCommand()
            logger.info(f"🔍 [PROXY] Created command, executing...")
            result = await cmd.execute(request)
            logger.info(f"🔍 [PROXY] Command executed, result type: {type(result).__name__}")
            if isinstance(result, ErrorResult):
                logger.error(f"🔍 [PROXY] Registration failed: {result.message}")
                return JSONResponse(
                    status_code=400, content={"status": "error", "detail": result.message}
                )
            logger.info(f"🔍 [PROXY] Registration successful, server_id={result.server_id}")
        except Exception as e:
            logger.error(f"🔍 [PROXY] Error executing command: {e}", exc_info=True)
            raise
        
        # result is SuccessResult (ProxyRegisterResult)
        if isinstance(result, SuccessResult):
            return JSONResponse(
                content={"status": "ok", "registered": result.server_id}
            )
        return JSONResponse(
            status_code=400, content={"status": "error", "detail": result.error}
        )

    @compatibility_router.post("/unregister")
    async def unregister_rest(request: dict):  # type: ignore[name-defined]
        """REST endpoint for unregistration (backward compatibility)."""
        from mcp_proxy_adapter.examples.full_application.proxy_commands import (
            ProxyUnregisterCommand,
        )

        cmd = ProxyUnregisterCommand()
        result = await cmd.execute(request)
        if isinstance(result, ErrorResult):
            return JSONResponse(
                status_code=400, content={"status": "error", "detail": result.message}
            )
        if isinstance(result, SuccessResult):
            return JSONResponse(
                content={"status": "ok", "unregistered": result.server_id}
            )
        return JSONResponse(
            status_code=400, content={"status": "error", "detail": result.error}
        )

    @compatibility_router.post("/proxy/heartbeat")
    async def heartbeat_rest(request: dict):  # type: ignore[name-defined]
        """REST endpoint for heartbeat (backward compatibility)."""
        from mcp_proxy_adapter.examples.full_application.proxy_commands import (
            ProxyHeartbeatCommand,
        )

        cmd = ProxyHeartbeatCommand()
        result = await cmd.execute(request)
        if isinstance(result, ErrorResult):
            return JSONResponse(
                status_code=404, content={"status": "error", "detail": result.message}
            )
        if isinstance(result, SuccessResult):
            return JSONResponse(
                content={"status": "ok", "heartbeat": result.server_id}
            )
        return JSONResponse(
            status_code=404, content={"status": "error", "detail": result.error}
        )

    @compatibility_router.get("/servers")
    async def servers_rest():  # type: ignore[name-defined]
        """REST endpoint for listing servers (backward compatibility)."""
        servers = []
        for server_id, instances in _registry.items():
            for instance_key, server_data in instances.items():
                servers.append(
                    {
                        "server_id": server_data.get("server_id", server_id),
                        "server_url": server_data.get("server_url", ""),
                        "capabilities": server_data.get("capabilities", []),
                        "metadata": server_data.get("metadata", {}),
                    }
                )
        return JSONResponse(content=servers)

    app.include_router(compatibility_router)

    port = int(app_config.get("server", {}).get("port", 3004))
    host = app_config.get("server", {}).get("host", args.host)

    # Setup graceful shutdown
    def signal_handler(signum, frame):  # type: ignore[no-redef]
        print("\n🛑 Proxy server stopping...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("🚀 Starting MCP Proxy Server (built on adapter)...")
    print(f"📡 Server URL: http://{host}:{port}")
    print("📋 Supported endpoints:")
    print("   JSON-RPC: proxy_register, proxy_unregister, proxy_heartbeat, proxy_list")
    print("   REST (compatibility): POST /register, POST /unregister, POST /proxy/heartbeat, GET /servers")
    print("⚡ Press Ctrl+C to stop\n")

    async def _run():
        """Run server using adapter's server engine."""
        try:
            engine = ServerEngineFactory.get_engine("hypercorn")
            if not engine:
                raise RuntimeError("Hypercorn engine not available")

            from hypercorn.asyncio import serve
            from hypercorn.config import Config as HypercornConfig

            hypercorn_config = HypercornConfig()
            hypercorn_config.bind = [f"{host}:{port}"]
            hypercorn_config.loglevel = "info"

            await serve(app, hypercorn_config)
        finally:
            pass

    asyncio.run(_run())


if __name__ == "__main__":
    main()
