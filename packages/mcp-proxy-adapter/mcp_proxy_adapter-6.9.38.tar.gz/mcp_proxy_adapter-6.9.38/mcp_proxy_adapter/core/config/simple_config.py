"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Simple configuration data container and IO helpers for MCP Proxy Adapter.

This module provides a minimal, explicit configuration model with three
sections: server, proxy_client and auth.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ServerConfig:
    host: str
    port: int
    protocol: str  # http | https | mtls
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    ca_cert_file: Optional[str] = None
    crl_file: Optional[str] = None
    log_dir: str = "./logs"


@dataclass
class HeartbeatConfig:
    endpoint: str = "/heartbeat"
    interval: int = 30


@dataclass
class RegistrationConfig:
    register_endpoint: str = "/register"
    unregister_endpoint: str = "/unregister"
    auto_on_startup: bool = True
    auto_on_shutdown: bool = True


@dataclass
class ProxyClientConfig:
    enabled: bool = False
    host: str = "localhost"
    port: int = 3005
    protocol: str = "http"
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    ca_cert_file: Optional[str] = None
    crl_file: Optional[str] = None
    heartbeat: HeartbeatConfig = field(default_factory=HeartbeatConfig)
    registration: RegistrationConfig = field(default_factory=RegistrationConfig)


@dataclass
class AuthConfig:
    use_token: bool = False
    use_roles: bool = False
    tokens: Dict[str, List[str]] = field(default_factory=dict)
    roles: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class SimpleConfigModel:
    server: ServerConfig
    proxy_client: ProxyClientConfig = field(default_factory=ProxyClientConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)


class SimpleConfig:
    """High-level loader/saver for SimpleConfigModel."""

    def __init__(self, config_path: str = "config.json") -> None:
        self.config_path: Path = Path(config_path)
        self.model: Optional[SimpleConfigModel] = None

    def load(self) -> SimpleConfigModel:
        content = json.loads(self.config_path.read_text(encoding="utf-8"))
        server = ServerConfig(**content["server"])  # type: ignore[arg-type]
        proxy_client = ProxyClientConfig(**content.get("proxy_client", {}))  # type: ignore[arg-type]
        # Nested structures for proxy client (heartbeat/registration)
        if isinstance(content.get("proxy_client"), dict):
            pc = content["proxy_client"]
            if isinstance(pc.get("heartbeat"), dict):
                proxy_client.heartbeat = HeartbeatConfig(**pc["heartbeat"])  # type: ignore[arg-type]
            if isinstance(pc.get("registration"), dict):
                proxy_client.registration = RegistrationConfig(**pc["registration"])  # type: ignore[arg-type]
        auth = AuthConfig(**content.get("auth", {}))  # type: ignore[arg-type]
        self.model = SimpleConfigModel(server=server, proxy_client=proxy_client, auth=auth)
        return self.model

    def save(self, out_path: Optional[str] = None) -> None:
        if self.model is None:
            raise ValueError("Configuration model is not loaded")
        path = Path(out_path) if out_path else self.config_path
        data: Dict[str, Any] = {
            "server": vars(self.model.server),
            "proxy_client": {
                **{k: v for k, v in vars(self.model.proxy_client).items() if k not in {"heartbeat", "registration"}},
                "heartbeat": vars(self.model.proxy_client.heartbeat),
                "registration": vars(self.model.proxy_client.registration),
            },
            "auth": vars(self.model.auth),
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


