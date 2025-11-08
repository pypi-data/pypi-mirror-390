#!/usr/bin/env python3
"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Lightweight local proxy server for MCP Proxy Adapter examples.

This server provides proxy registration endpoints at /proxy for adapter instances
to register/unregister/heartbeat and for simple discovery.
"""

import argparse
import asyncio
import signal
import sys
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Simple in-memory storage for registered adapters
registered_adapters: Dict[str, Dict] = {}


class AdapterRegistration(BaseModel):
    name: str
    url: str
    capabilities: List[str]
    metadata: Optional[Dict] = {}


class ProxyRouter:
    """Simple proxy router for MCP examples."""

    def __init__(self):
        self.app = FastAPI(title="MCP Local Proxy", version="1.0.0")
        self._setup_routes()

    def _setup_routes(self):
        @self.app.post("/register")
        def register(adapter: AdapterRegistration):  # type: ignore[name-defined]
            registered_adapters[adapter.name] = adapter.dict()
            return {"status": "ok", "registered": adapter.name}

        @self.app.post("/unregister")
        def unregister(adapter: AdapterRegistration):  # type: ignore[name-defined]
            registered_adapters.pop(adapter.name, None)
            return {"status": "ok", "unregistered": adapter.name}

        @self.app.post("/proxy/heartbeat")
        def heartbeat(adapter: AdapterRegistration):  # type: ignore[name-defined]
            if adapter.name in registered_adapters:
                return {"status": "ok", "heartbeat": adapter.name}
            raise HTTPException(status_code=404, detail="Adapter not registered")

        @self.app.get("/proxy/list")
        def list_registered():
            return {"servers": list(registered_adapters.values())}

        @self.app.get("/proxy/health")
        def proxy_health():
            return {"status": "ok", "model": "mcp-local-proxy", "version": "1.0.0"}

        # Compatibility endpoint expected by test instructions
        @self.app.get("/servers")
        def servers_plain():
            return list(registered_adapters.values())


def create_proxy_app() -> FastAPI:
    """Create FastAPI app with proxy endpoints."""
    router = ProxyRouter()
    return router.app


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run local proxy server for MCP examples"
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=3004, help="Port to bind to (default: 3004)"
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Log level",
    )

    args = parser.parse_args()

    # Create FastAPI app
    app = create_proxy_app()

    # Setup graceful shutdown
    def signal_handler(signum, frame):  # type: ignore[no-redef]
        print("\n🛑 Proxy server stopping...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("🚀 Starting MCP Local Proxy Server...")
    print(f"📡 Server URL: http://{args.host}:{args.port}")
    print(f"🔗 Proxy endpoints available at: http://{args.host}:{args.port}/proxy")
    print("📋 Supported endpoints:")
    print("   POST /proxy/register    - Register adapter")
    print("   POST /proxy/unregister  - Unregister adapter")
    print("   GET  /proxy/list        - List registered adapters")
    print("   GET  /proxy/health      - Health check")
    print("   POST /proxy/heartbeat   - Heartbeat from adapter")
    print("⚡ Press Ctrl+C to stop\n")

    # Run server with Hypercorn
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = [f"{args.host}:{args.port}"]
    config.loglevel = args.log_level

    asyncio.run(serve(app, config))


if __name__ == "__main__":
    main()
