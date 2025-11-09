"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Simple configuration data container and IO helpers for MCP Proxy Adapter.

This module provides a minimal, explicit configuration model with three
sections: server, client, registration and auth.

- server: Server endpoint configuration (listening for incoming connections)
- client: Client configuration (for connecting to external servers)
- registration: Proxy registration configuration (for registering with proxy server)
- auth: Authentication and authorization configuration
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ServerConfig:
    """Server endpoint configuration (listening for incoming connections)."""

    host: str
    port: int
    protocol: str  # http | https | mtls
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    ca_cert_file: Optional[str] = None
    crl_file: Optional[str] = None
    use_system_ca: bool = (
        False  # If True, allow system CA store when ca_cert_file is not provided
    )
    log_dir: str = "./logs"


@dataclass
class ClientConfig:
    """Client configuration (for connecting to external servers)."""

    enabled: bool = False
    protocol: str = "http"  # http | https | mtls
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    ca_cert_file: Optional[str] = None
    crl_file: Optional[str] = None
    use_system_ca: bool = (
        False  # If True, allow system CA store when ca_cert_file is not provided
    )


@dataclass
class HeartbeatConfig:
    endpoint: str = "/heartbeat"
    interval: int = 30


@dataclass
class RegistrationConfig:
    """Proxy registration configuration (for registering with proxy server)."""

    enabled: bool = False
    host: str = "localhost"
    port: int = 3005
    protocol: str = "http"  # http | https | mtls
    server_id: Optional[str] = None  # Server identifier for registration (preferred)
    server_name: Optional[str] = None  # Legacy field, use server_id instead
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    ca_cert_file: Optional[str] = None
    crl_file: Optional[str] = None
    use_system_ca: bool = (
        False  # If True, allow system CA store when ca_cert_file is not provided
    )
    register_endpoint: str = "/register"
    unregister_endpoint: str = "/unregister"
    auto_on_startup: bool = True
    auto_on_shutdown: bool = True
    heartbeat: HeartbeatConfig = field(default_factory=HeartbeatConfig)


@dataclass
class AuthConfig:
    use_token: bool = False
    use_roles: bool = False
    tokens: Dict[str, List[str]] = field(default_factory=dict)
    roles: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class SimpleConfigModel:
    server: ServerConfig
    client: ClientConfig = field(default_factory=ClientConfig)
    registration: RegistrationConfig = field(default_factory=RegistrationConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)


class SimpleConfig:
    """High-level loader/saver for SimpleConfigModel."""

    def __init__(self, config_path: str = "config.json") -> None:
        self.config_path: Path = Path(config_path)
        self.model: Optional[SimpleConfigModel] = None

    def load(self) -> SimpleConfigModel:
        content = json.loads(self.config_path.read_text(encoding="utf-8"))
        # Filter out unknown fields from server config (like debug, log_level from old format)
        server_data = content["server"].copy()
        # Remove fields that are not in ServerConfig
        known_fields = {
            "host",
            "port",
            "protocol",
            "cert_file",
            "key_file",
            "ca_cert_file",
            "crl_file",
            "use_system_ca",
            "log_dir",
        }
        server_data = {k: v for k, v in server_data.items() if k in known_fields}

        server = ServerConfig(**server_data)  # type: ignore[arg-type]

        # Load client config (new structure)
        client = ClientConfig(**content.get("client", {}))  # type: ignore[arg-type]

        # Load registration config (new structure)
        # Support backward compatibility: if proxy_client exists, migrate to registration
        registration_data = content.get("registration", {})
        if not registration_data and "proxy_client" in content:
            # Migrate from old proxy_client structure
            pc = content["proxy_client"]
            registration_data = {
                "enabled": pc.get("enabled", False),
                "host": pc.get("host", "localhost"),
                "port": pc.get("port", 3005),
                "protocol": pc.get("protocol", "http"),
                "server_id": pc.get("server_id"),
                "server_name": pc.get("server_name"),
                "cert_file": pc.get("cert_file"),
                "key_file": pc.get("key_file"),
                "ca_cert_file": pc.get("ca_cert_file"),
                "crl_file": pc.get("crl_file"),
                "use_system_ca": pc.get("use_system_ca", False),
                "register_endpoint": (
                    pc.get("registration", {}).get("register_endpoint", "/register")
                    if isinstance(pc.get("registration"), dict)
                    else "/register"
                ),
                "unregister_endpoint": (
                    pc.get("registration", {}).get("unregister_endpoint", "/unregister")
                    if isinstance(pc.get("registration"), dict)
                    else "/unregister"
                ),
                "auto_on_startup": (
                    pc.get("registration", {}).get("auto_on_startup", True)
                    if isinstance(pc.get("registration"), dict)
                    else True
                ),
                "auto_on_shutdown": (
                    pc.get("registration", {}).get("auto_on_shutdown", True)
                    if isinstance(pc.get("registration"), dict)
                    else True
                ),
                "heartbeat": pc.get("heartbeat", {}),
            }

        registration = RegistrationConfig(**registration_data)  # type: ignore[arg-type]
        # Handle nested heartbeat structure
        if isinstance(registration_data.get("heartbeat"), dict):
            registration.heartbeat = HeartbeatConfig(**registration_data["heartbeat"])  # type: ignore[arg-type]

        auth = AuthConfig(**content.get("auth", {}))  # type: ignore[arg-type]
        self.model = SimpleConfigModel(
            server=server, client=client, registration=registration, auth=auth
        )
        return self.model

    def save(self, out_path: Optional[str] = None) -> None:
        if self.model is None:
            raise ValueError("Configuration model is not loaded")
        path = Path(out_path) if out_path else self.config_path
        data: Dict[str, Any] = {
            "server": vars(self.model.server),
            "client": vars(self.model.client),
            "registration": {
                **{
                    k: v
                    for k, v in vars(self.model.registration).items()
                    if k != "heartbeat"
                },
                "heartbeat": vars(self.model.registration.heartbeat),
            },
            "auth": vars(self.model.auth),
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
