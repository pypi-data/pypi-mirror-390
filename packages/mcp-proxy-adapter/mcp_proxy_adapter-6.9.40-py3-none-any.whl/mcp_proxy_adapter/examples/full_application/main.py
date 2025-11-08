#!/usr/bin/env python3
"""
Full Application Example
This is a complete application that demonstrates all features of MCP Proxy Adapter framework:
- Built-in commands
- Custom commands
- Dynamically loaded commands
- Built-in command hooks
- Application hooks
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
import argparse
import asyncio
import json
from pathlib import Path

from mcp_proxy_adapter.api.app import create_app
from mcp_proxy_adapter.core.server_engine import ServerEngineFactory
from mcp_proxy_adapter.core.server_adapter import ServerConfigAdapter
from mcp_proxy_adapter.client.proxy import ProxyClient
from mcp_proxy_adapter.commands.command_registry import registry


def register_all_commands():
    """Register all available commands (built-in, load, queue)."""
    from mcp_proxy_adapter.commands.load_command import LoadCommand
    
    # Register load command
    registry._commands["load"] = LoadCommand
    registry._command_types["load"] = "builtin"
    
    # Register queue commands (will fail gracefully if queuemgr not available)
    try:
        from mcp_proxy_adapter.commands.queue_commands import (
            QueueAddJobCommand,
            QueueStartJobCommand,
            QueueStopJobCommand,
            QueueDeleteJobCommand,
            QueueGetJobStatusCommand,
            QueueListJobsCommand,
            QueueHealthCommand,
        )
        registry._commands["queue_add_job"] = QueueAddJobCommand
        registry._command_types["queue_add_job"] = "builtin"
        registry._commands["queue_start_job"] = QueueStartJobCommand
        registry._command_types["queue_start_job"] = "builtin"
        registry._commands["queue_stop_job"] = QueueStopJobCommand
        registry._command_types["queue_stop_job"] = "builtin"
        registry._commands["queue_delete_job"] = QueueDeleteJobCommand
        registry._command_types["queue_delete_job"] = "builtin"
        registry._commands["queue_get_job_status"] = QueueGetJobStatusCommand
        registry._command_types["queue_get_job_status"] = "builtin"
        registry._commands["queue_list_jobs"] = QueueListJobsCommand
        registry._command_types["queue_list_jobs"] = "builtin"
        registry._commands["queue_health"] = QueueHealthCommand
        registry._command_types["queue_health"] = "builtin"
        print("✅ Queue commands registered")
    except Exception as e:
        print(f"⚠️  Queue commands not available: {e}")


def main():
    """Minimal runnable entrypoint for full application example."""
    parser = argparse.ArgumentParser(description="MCP Proxy Adapter Full Application")
    parser.add_argument("--config", required=True, help="Path to configuration file")
    parser.add_argument("--port", type=int, help="Port to run server on (override)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    args = parser.parse_args()

    cfg_path = Path(args.config)
    if not cfg_path.exists():
        print(f"❌ Configuration file not found: {cfg_path}")
        raise SystemExit(1)

    try:
        with cfg_path.open("r", encoding="utf-8") as f:
            app_config = json.load(f)
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Failed to load configuration: {exc}")
        raise SystemExit(1)

    if args.port:
        app_config.setdefault("server", {}).update({"port": args.port})
        print(f"🔧 Overriding port to {args.port}")
    if args.host:
        app_config.setdefault("server", {}).update({"host": args.host})
        print(f"🔧 Overriding host to {args.host}")

    # Strict protocol checks: forbid any form of mTLS over HTTP
    proto = str(app_config.get("server", {}).get("protocol", "http")).lower()
    ssl_cfg = app_config.get("ssl", {}) or {}
    transport = app_config.get("transport", {}) or {}
    require_client_cert = bool(
        ssl_cfg.get("require_client_cert") or transport.get("verify_client")
    )

    # --- SimpleConfig compatibility bridge: synthesize ssl section when absent ---
    if not app_config.get("ssl") and isinstance(app_config.get("server"), dict):
        srv = app_config["server"]
        cert_file = srv.get("cert_file")
        key_file = srv.get("key_file")
        ca_file = srv.get("ca_cert_file")
        if cert_file and key_file:
            app_config["ssl"] = {
                "enabled": True,
                "cert_file": cert_file,
                "key_file": key_file,
            }
            if ca_file:
                app_config["ssl"]["ca_cert"] = ca_file
            # For mtls protocol, enforce client verification
            if proto == "mtls":
                app_config.setdefault("transport", {}).update({"verify_client": True})
        # Refresh local vars after synthesis
        ssl_cfg = app_config.get("ssl", {}) or {}
        transport = app_config.get("transport", {}) or {}
        require_client_cert = bool(
            ssl_cfg.get("require_client_cert") or transport.get("verify_client")
        )
    # ---------------------------------------------------------------------------

    if proto == "http":
        if require_client_cert:
            raise SystemExit(
                "CRITICAL CONFIG ERROR: mTLS (client certificate verification) cannot be used with HTTP. "
                "Switch protocol to 'mtls' (or 'https' without client verification), and configure SSL certificates."
            )

    if proto == "mtls":
        if not ssl_cfg.get("enabled"):
            raise SystemExit(
                "CRITICAL CONFIG ERROR: Protocol 'mtls' requires SSL to be enabled."
            )
        if not require_client_cert:
            raise SystemExit(
                "CRITICAL CONFIG ERROR: Protocol 'mtls' requires client certificate verification. "
                "Set ssl.require_client_cert=true or transport.verify_client=true."
            )
        cert = ssl_cfg.get("certfile") or ssl_cfg.get("cert_file")
        key = ssl_cfg.get("keyfile") or ssl_cfg.get("key_file")
        ca = ssl_cfg.get("cafile") or ssl_cfg.get("ca_cert") or ssl_cfg.get("ca_cert_file")
        if not (cert and key and ca):
            raise SystemExit(
                "CRITICAL CONFIG ERROR: 'mtls' requires ssl.certfile/keyfile (or cert_file/key_file) and CA certificate."
            )

    app = create_app(title="Full Application Example", description="Complete MCP Proxy Adapter with all features", version="1.0.0", app_config=app_config, config_path=str(cfg_path))

    port = int(app_config.get("server", {}).get("port", 8080))
    host = app_config.get("server", {}).get("host", args.host)

    print("🚀 Starting Full Application Example")
    print(f"📋 Configuration: {cfg_path}")
    print("============================================================")
    
    # Register all commands
    register_all_commands()
    print(f"📋 Registered commands: {', '.join(sorted(registry.get_all_commands().keys()))}")

    # Prepare server configuration for ServerEngine
    server_config = {
        "host": host,
        "port": port,
        "log_level": "info",
        "reload": False,
    }
    
    # Add SSL configuration if enabled
    ssl_cfg = app_config.get("ssl", {})
    if ssl_cfg.get("enabled"):
        cert = ssl_cfg.get("certfile") or ssl_cfg.get("cert_file")
        key = ssl_cfg.get("keyfile") or ssl_cfg.get("key_file")
        ca = ssl_cfg.get("cafile") or ssl_cfg.get("ca_cert") or ssl_cfg.get("ca_cert_file")
        if cert and key:
            server_config["certfile"] = cert
            server_config["keyfile"] = key
        if ca:
            server_config["ca_certs"] = ca
        if ssl_cfg.get("verify_client") or app_config.get("transport", {}).get("verify_client"):
            server_config["verify_mode"] = 2  # ssl.CERT_REQUIRED
        if "chk_hostname" in ssl_cfg:
            server_config["check_hostname"] = ssl_cfg["chk_hostname"]

    # Optional proxy registration
    pr = (app_config.get("proxy_registration") or {}) if isinstance(app_config, dict) else {}
    name = pr.get("server_id") or pr.get("server_name") or "mcp-adapter"
    scheme = "https" if str(app_config.get("server", {}).get("protocol", "http")) in ("https", "mtls") else "http"
    advertised_host = app_config.get("server", {}).get("advertised_host") or "mcp-adapter"
    advertised_url = f"{scheme}://{advertised_host}:{port}"

    async def _run():
        """Run server with proxy registration and heartbeat."""
        heartbeat_task = None
        try:
            if pr.get("enabled") and pr.get("proxy_url"):
                pc = ProxyClient(pr["proxy_url"])
                try:
                    pc.register(name=name, url=advertised_url, capabilities=["jsonrpc"], metadata={})
                    print(f"✅ Registered on proxy as {name} -> {advertised_url}")
                except Exception as exc:  # noqa: BLE001
                    print(f"⚠️  Proxy registration failed: {exc}")

                async def _hb():
                    interval = int((pr.get("heartbeat") or {}).get("interval", 15))
                    while True:
                        try:
                            pc.heartbeat(name=name, url=advertised_url)
                        except Exception:
                            pass
                        await asyncio.sleep(max(2, interval))

                heartbeat_task = asyncio.create_task(_hb())

            # Use ServerEngine with hypercorn (via ServerEngineFactory)
            engine = ServerEngineFactory.get_engine("hypercorn")
            if not engine:
                raise RuntimeError("Hypercorn engine not available")
            
            # Convert SSL config if needed
            if "ssl" in app_config:
                ssl_converted = ServerConfigAdapter.convert_ssl_config_for_engine(
                    app_config["ssl"], "hypercorn"
                )
                server_config.update(ssl_converted)
            
            # Run server using hypercorn engine
            # Use create_task instead of run_server to avoid nested event loop
            from hypercorn.asyncio import serve
            from hypercorn.config import Config as HypercornConfig
            
            hypercorn_config = HypercornConfig()
            hypercorn_config.bind = [f"{host}:{port}"]
            hypercorn_config.loglevel = "info"
            
            # Add SSL configuration if enabled
            if ssl_cfg.get("enabled"):
                cert = ssl_cfg.get("certfile") or ssl_cfg.get("cert_file")
                key = ssl_cfg.get("keyfile") or ssl_cfg.get("key_file")
                ca = ssl_cfg.get("cafile") or ssl_cfg.get("ca_cert") or ssl_cfg.get("ca_cert_file")
                if cert and key:
                    hypercorn_config.certfile = cert
                    hypercorn_config.keyfile = key
                if ca:
                    hypercorn_config.ca_certs = ca
                if ssl_cfg.get("verify_client") or app_config.get("transport", {}).get("verify_client"):
                    hypercorn_config.verify_mode = 2  # ssl.CERT_REQUIRED
            
            await serve(app, hypercorn_config)
        finally:
            if heartbeat_task:
                heartbeat_task.cancel()
            if pr.get("enabled") and pr.get("proxy_url"):
                try:
                    ProxyClient(pr["proxy_url"]).unregister(name)
                    print(f"🛑 Unregistered from proxy: {name}")
                except Exception:
                    pass

    asyncio.run(_run())


if __name__ == "__main__":
    main()
