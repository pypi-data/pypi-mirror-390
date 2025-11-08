"""Registration helper context builders for proxy interactions.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


@dataclass
class ProxyCredentials:
    """Client certificate and verification settings for proxy communication."""

    cert: Optional[Tuple[str, str]]
    verify: Union[bool, str]


@dataclass
class RegistrationContext:
    """Prepared data required to register the adapter with a proxy."""

    server_name: str
    advertised_url: str
    proxy_url: str
    register_endpoint: str
    capabilities: List[str]
    metadata: Dict[str, Any]
    use_proxy_client: bool
    proxy_client_config: Dict[str, Any]
    proxy_registration_config: Dict[str, Any]
    credentials: ProxyCredentials


@dataclass
class HeartbeatSettings:
    """Configuration for heartbeat scheduling."""

    interval: int
    endpoint: str


def prepare_registration_context(
    config: Dict[str, Any], logger: Any
) -> Optional[RegistrationContext]:
    """Build registration context from configuration.

    Returns ``None`` when registration should not be performed.
    """

    proxy_client_config = dict(config.get("proxy_client") or {})
    proxy_registration_config = dict(config.get("proxy_registration") or {})
    use_proxy_client = bool(proxy_client_config)

    if use_proxy_client:
        registration_config = proxy_client_config.get("registration") or {}
        registration_enabled = registration_config.get("auto_on_startup", False)
    else:
        registration_config = proxy_registration_config
        registration_enabled = proxy_registration_config.get("enabled", False)

    if not registration_enabled:
        logger.info(
            "Proxy registration disabled (auto_on_startup=false or enabled=false)"
        )
        return None

    if use_proxy_client:
        proxy_host = proxy_client_config.get("host", "localhost")
        proxy_port = proxy_client_config.get("port", 3005)
        proxy_scheme = "http"
        proxy_base_url = f"{proxy_scheme}://{proxy_host}:{proxy_port}"
        register_endpoint = registration_config.get("register_endpoint", "/register")
        if register_endpoint.startswith("/proxy/"):
            proxy_url = f"{proxy_base_url}/proxy"
        else:
            proxy_url = proxy_base_url
    else:
        proxy_url_candidate = (
            proxy_registration_config.get("proxy_url")
            or proxy_registration_config.get("server_url")
        )
        if not proxy_url_candidate:
            logger.warning("No proxy server URL configured")
            return None
        proxy_url = str(proxy_url_candidate)
        register_endpoint = "/register"

    server_config = dict(config.get("server") or {})
    host = server_config.get("host", "127.0.0.1")
    port = server_config.get("port", 8000)
    protocol = server_config.get("protocol", "http")
    advertised_host = server_config.get("advertised_host") or host
    scheme = "https" if protocol in ("https", "mtls") else "http"
    advertised_url = f"{scheme}://{advertised_host}:{port}"

    if use_proxy_client:
        server_name = proxy_client_config.get("server_id") or proxy_client_config.get(
            "server_name"
        )
        server_name = server_name or f"mcp-adapter-{host}-{port}"
        capabilities = proxy_client_config.get("capabilities", ["jsonrpc", "health"])
        metadata = {
            "uuid": config.get("uuid"),
            "protocol": protocol,
            "host": host,
            "port": port,
            **(proxy_client_config.get("metadata") or {}),
        }
    else:
        server_name = proxy_registration_config.get(
            "server_id"
        ) or proxy_registration_config.get("server_name")
        server_name = server_name or f"mcp-adapter-{host}-{port}"
        capabilities = proxy_registration_config.get(
            "capabilities", ["jsonrpc", "health"]
        )
        metadata = {
            "uuid": config.get("uuid"),
            "protocol": protocol,
            "host": host,
            "port": port,
            **(proxy_registration_config.get("metadata") or {}),
        }

    credentials = _resolve_registration_credentials(
        use_proxy_client, proxy_client_config, proxy_registration_config
    )

    return RegistrationContext(
        server_name=server_name,
        advertised_url=advertised_url,
        proxy_url=proxy_url,
        register_endpoint=register_endpoint,
        capabilities=capabilities,
        metadata=metadata,
        use_proxy_client=use_proxy_client,
        proxy_client_config=proxy_client_config,
        proxy_registration_config=proxy_registration_config,
        credentials=credentials,
    )


def resolve_runtime_credentials(
    use_proxy_client: bool,
    proxy_client_config: Dict[str, Any],
    proxy_registration_config: Dict[str, Any],
) -> ProxyCredentials:
    """Return credentials for runtime interactions (heartbeat, unregister)."""

    if use_proxy_client:
        cert_tuple = _build_cert_tuple(
            proxy_client_config.get("cert_file"),
            proxy_client_config.get("key_file"),
        )
        proxy_protocol = proxy_client_config.get("protocol", "http")
        ca_cert = proxy_client_config.get("ca_cert_file")

        verify: Union[bool, str] = True
        if proxy_protocol == "http":
            verify = False
        elif ca_cert:
            verify = ca_cert

        return ProxyCredentials(cert=cert_tuple, verify=verify)

    return _resolve_registration_credentials(False, {}, proxy_registration_config)


def resolve_heartbeat_settings(
    use_proxy_client: bool,
    proxy_client_config: Dict[str, Any],
    proxy_registration_config: Dict[str, Any],
) -> HeartbeatSettings:
    """Compute heartbeat interval and endpoint."""

    if use_proxy_client:
        heartbeat_config = proxy_client_config.get("heartbeat") or {}
        interval = int(heartbeat_config.get("interval", 30))
        endpoint = heartbeat_config.get("endpoint", "/heartbeat")
    else:
        heartbeat_config = proxy_registration_config.get("heartbeat") or {}
        interval = int(
            heartbeat_config.get(
                "interval", proxy_registration_config.get("heartbeat_interval", 30)
            )
        )
        endpoint = "/heartbeat"

    return HeartbeatSettings(interval=interval, endpoint=endpoint)


def resolve_unregister_endpoint(
    use_proxy_client: bool,
    proxy_client_config: Dict[str, Any],
) -> str:
    """Get unregister endpoint path."""

    if use_proxy_client:
        registration_config = proxy_client_config.get("registration") or {}
        endpoint = registration_config.get("unregister_endpoint")
        if endpoint:
            return str(endpoint)
        return "/unregister"
    return "/unregister"


def _resolve_registration_credentials(
    use_proxy_client: bool,
    proxy_client_config: Dict[str, Any],
    proxy_registration_config: Dict[str, Any],
) -> ProxyCredentials:
    if use_proxy_client:
        # Test proxy uses HTTP in current setup, credentials are not required.
        return ProxyCredentials(cert=None, verify=False)

    cert_config = proxy_registration_config.get("certificate") or {}
    ssl_config = proxy_registration_config.get("ssl") or {}

    cert_tuple = _build_cert_tuple(
        cert_config.get("cert_file"),
        cert_config.get("key_file"),
    )

    verify: Union[bool, str] = True
    ca_cert = ssl_config.get("ca_cert")
    verify_mode = ssl_config.get("verify_mode", "CERT_REQUIRED")
    if verify_mode == "CERT_NONE":
        verify = False
    elif ca_cert:
        verify = ca_cert

    return ProxyCredentials(cert=cert_tuple, verify=verify)


def _build_cert_tuple(
    cert_file: Optional[str],
    key_file: Optional[str],
) -> Optional[Tuple[str, str]]:
    if not cert_file or not key_file:
        return None

    cert_path = Path(cert_file)
    key_path = Path(key_file)
    if not cert_path.exists() or not key_path.exists():
        return None

    return (str(cert_path.absolute()), str(key_path.absolute()))
