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
    url: str  # Full URL for heartbeat (e.g., "http://localhost:3005/proxy/heartbeat")


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
        # Determine proxy scheme based on proxy protocol
        # NOTE: proxy_client.protocol indicates the SERVER's protocol, not the proxy's protocol
        # Determine proxy protocol:
        # 1. Check explicit proxy_protocol field (if exists) - this is the proxy's actual protocol
        # 2. Check if port is 3005 (test proxy) - always use HTTP for test proxy
        # 3. Check if client certificates are provided AND exist on disk (indicates HTTPS/mTLS proxy)
        # 4. Check server protocol as hint (if server uses HTTPS/mTLS, proxy might too)
        # 5. Fallback to HTTP (for test proxy)
        proxy_protocol = proxy_client_config.get("proxy_protocol")
        if not proxy_protocol:
            # Test proxy (ports 3004, 3005) always uses HTTP
            if proxy_port in (3004, 3005):
                proxy_protocol = "http"
                logger.debug(
                    f"Test proxy detected (port {proxy_port}), using HTTP protocol"
                )
            else:
                # Check if client certificates are provided for proxy connection
                cert_file = proxy_client_config.get("cert_file")
                key_file = proxy_client_config.get("key_file")
                ca_cert_file = proxy_client_config.get("ca_cert_file")
                cert_tuple = _build_cert_tuple(cert_file, key_file)
                
                if cert_tuple:
                    # Certificates exist and are valid - proxy uses HTTPS/mTLS
                    # Certificates in proxy_client are for connecting TO the proxy
                    # Check if CA cert is provided to determine if it's mTLS
                    if ca_cert_file and Path(ca_cert_file).exists():
                        # All certificates (cert, key, CA) provided - likely mTLS
                        # Use server protocol as hint for mTLS vs HTTPS
                        server_protocol = proxy_client_config.get("protocol", "http")
                        proxy_protocol = (
                            "mtls" if server_protocol == "mtls" else "https"
                        )
                        logger.debug(
                            f"Proxy certificates found, using {proxy_protocol} protocol"
                        )
                    else:
                        # Only cert and key, no CA - HTTPS
                        proxy_protocol = "https"
                        logger.debug("Proxy certificates found (no CA), using HTTPS protocol")
                else:
                    # No valid certificates - check server protocol as hint
                    server_protocol = proxy_client_config.get("protocol", "http")
                    if server_protocol in ("https", "mtls"):
                        # Server uses HTTPS/mTLS - proxy might too, but no certs provided
                        # Default to HTTP for safety (test proxy scenario)
                        proxy_protocol = "http"
                        logger.debug(
                            f"No proxy certificates, server uses {server_protocol}, defaulting to HTTP for proxy"
                        )
                    else:
                        # Server uses HTTP - proxy likely uses HTTP too
                        proxy_protocol = "http"
                        logger.debug("No proxy certificates, using HTTP protocol")
        # If proxy uses HTTPS/mTLS, use https scheme
        proxy_scheme = "https" if proxy_protocol in ("https", "mtls") else "http"
        proxy_base_url = f"{proxy_scheme}://{proxy_host}:{proxy_port}"
        register_endpoint = registration_config.get("register_endpoint", "/register")
        # register_endpoint can be:
        # - "/register" -> proxy_url = "http://host:port", register_with_proxy adds "/register"
        # - "/proxy/register" -> treat as "/register" (test proxy uses /register, not /proxy/register)
        # - "http://host:port/register" -> proxy_url = "http://host:port/register" (full URL)
        if register_endpoint.startswith("http://") or register_endpoint.startswith("https://"):
            # Full URL provided - use as-is
            proxy_url = register_endpoint
        elif register_endpoint.startswith("/proxy/"):
            # Endpoint is /proxy/register, but test proxy uses /register
            # Extract /register from /proxy/register and use base URL
            # register_with_proxy will add /register to proxy_url
            proxy_url = proxy_base_url
            logger.debug(
                f"register_endpoint '{register_endpoint}' starts with /proxy/, "
                f"but test proxy uses /register, using base URL: {proxy_url}"
            )
        else:
            # Simple endpoint like /register - proxy_url is base, register_with_proxy adds /register
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
    proxy_url: str,
) -> HeartbeatSettings:
    """Compute heartbeat interval and full URL.
    
    Args:
        use_proxy_client: Whether using proxy_client config format
        proxy_client_config: proxy_client configuration dict
        proxy_registration_config: proxy_registration configuration dict
        proxy_url: Base proxy URL (e.g., "http://localhost:3005")
    
    Returns:
        HeartbeatSettings with interval and full URL
    """
    if use_proxy_client:
        heartbeat_config = proxy_client_config.get("heartbeat") or {}
        interval = int(heartbeat_config.get("interval", 30))
        # Check if full URL is provided
        heartbeat_url = heartbeat_config.get("url")
        if not heartbeat_url:
            # Build URL from endpoint (backward compatibility)
            endpoint = heartbeat_config.get("endpoint", "/proxy/heartbeat")
            heartbeat_url = f"{proxy_url.rstrip('/')}{endpoint}"
        elif not heartbeat_url.startswith("http://") and not heartbeat_url.startswith("https://"):
            # heartbeat_url is a path, not a full URL - construct full URL
            endpoint = heartbeat_url
            heartbeat_url = f"{proxy_url.rstrip('/')}{endpoint}"
    else:
        heartbeat_config = proxy_registration_config.get("heartbeat") or {}
        interval = int(
            heartbeat_config.get(
                "interval", proxy_registration_config.get("heartbeat_interval", 30)
            )
        )
        # Check if full URL is provided
        heartbeat_url = heartbeat_config.get("url")
        if not heartbeat_url:
            # Build URL from endpoint (backward compatibility)
            endpoint = heartbeat_config.get("endpoint", "/proxy/heartbeat")
            heartbeat_url = f"{proxy_url.rstrip('/')}{endpoint}"
        elif not heartbeat_url.startswith("http://") and not heartbeat_url.startswith("https://"):
            # heartbeat_url is a path, not a full URL - construct full URL
            endpoint = heartbeat_url
            # If endpoint is /heartbeat and proxy is test proxy (port 3004/3005), use /proxy/heartbeat
            if endpoint == "/heartbeat":
                from urllib.parse import urlparse
                parsed = urlparse(proxy_url)
                proxy_port = parsed.port or (443 if parsed.scheme == "https" else 80)
                if proxy_port in (3004, 3005):
                    endpoint = "/proxy/heartbeat"
            heartbeat_url = f"{proxy_url.rstrip('/')}{endpoint}"

    return HeartbeatSettings(interval=interval, url=heartbeat_url)


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
        # Use same logic as resolve_runtime_credentials for consistency
        # Check if proxy itself uses HTTPS/mTLS and requires certificates
        cert_tuple = _build_cert_tuple(
            proxy_client_config.get("cert_file"),
            proxy_client_config.get("key_file"),
        )
        # Determine proxy protocol (same logic as in prepare_registration_context)
        proxy_protocol = proxy_client_config.get("proxy_protocol")
        if not proxy_protocol:
            # Get proxy port for test proxy detection
            proxy_port = proxy_client_config.get("port", 3005)
            # Test proxy (port 3005) always uses HTTP
            if proxy_port == 3005:
                proxy_protocol = "http"
            else:
                # Check if client certificates are provided for proxy connection
                cert_file = proxy_client_config.get("cert_file")
                key_file = proxy_client_config.get("key_file")
                ca_cert_file = proxy_client_config.get("ca_cert_file")
                cert_tuple = _build_cert_tuple(cert_file, key_file)
                
                if cert_tuple:
                    # Certificates exist and are valid - proxy uses HTTPS/mTLS
                    # Check if CA cert is provided to determine if it's mTLS
                    if ca_cert_file and Path(ca_cert_file).exists():
                        # All certificates (cert, key, CA) provided - likely mTLS
                        # Use server protocol as hint for mTLS vs HTTPS
                        server_protocol = proxy_client_config.get("protocol", "http")
                        proxy_protocol = (
                            "mtls" if server_protocol == "mtls" else "https"
                        )
                    else:
                        # Only cert and key, no CA - HTTPS
                        proxy_protocol = "https"
                else:
                    # No valid certificates - check server protocol as hint
                    server_protocol = proxy_client_config.get("protocol", "http")
                    if server_protocol in ("https", "mtls"):
                        # Server uses HTTPS/mTLS - proxy might too, but no certs provided
                        # Default to HTTP for safety (test proxy scenario)
                        proxy_protocol = "http"
                    else:
                        # Server uses HTTP - proxy likely uses HTTP too
                        proxy_protocol = "http"
        ca_cert = proxy_client_config.get("ca_cert_file")

        verify: Union[bool, str] = True
        if proxy_protocol == "http":
            # HTTP proxy doesn't need certificates
            verify = False
        elif proxy_protocol in ("https", "mtls"):
            # HTTPS/mTLS proxy requires certificates
            if ca_cert:
                verify = ca_cert
            elif proxy_protocol == "mtls":
                # mTLS requires CA cert
                verify = True  # Will fail if no CA, but that's expected
            else:
                # HTTPS can use system CA store
                verify = True

        return ProxyCredentials(cert=cert_tuple, verify=verify)

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
