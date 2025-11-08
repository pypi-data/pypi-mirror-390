"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Simple configuration validator ensuring required fields and files exist.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

from .simple_config import SimpleConfigModel
from mcp_proxy_adapter.core.certificate.certificate_validator import (
    CertificateValidator,
)


@dataclass
class ValidationError:
    message: str


class SimpleConfigValidator:
    """Validate SimpleConfigModel instances."""

    def validate(self, model: SimpleConfigModel) -> List[ValidationError]:
        errors: List[ValidationError] = []
        errors.extend(self._validate_server(model))
        errors.extend(self._validate_proxy_client(model))
        errors.extend(self._validate_auth(model))
        return errors

    def _validate_server(self, model: SimpleConfigModel) -> List[ValidationError]:
        e: List[ValidationError] = []
        s = model.server
        if not s.host:
            e.append(ValidationError("server.host is required"))
        if not isinstance(s.port, int):  # type: ignore[unreachable]
            e.append(ValidationError("server.port must be integer"))
        if s.protocol not in ("http", "https", "mtls"):
            e.append(
                ValidationError("server.protocol must be one of: http, https, mtls")
            )
        # Protocol-specific certificate requirements
        if s.protocol == "mtls":
            # For mtls: all certificates are required
            if not s.cert_file:
                e.append(
                    ValidationError("server.cert_file is required for mtls protocol")
                )
            if not s.key_file:
                e.append(
                    ValidationError("server.key_file is required for mtls protocol")
                )
            if not s.ca_cert_file:
                e.append(
                    ValidationError("server.ca_cert_file is required for mtls protocol")
                )
        elif s.protocol == "https":
            # For https: certificates are optional, but if one is specified, both must be
            if (s.cert_file and not s.key_file) or (s.key_file and not s.cert_file):
                e.append(
                    ValidationError(
                        "server.cert_file and server.key_file must both be specified or both omitted for https"
                    )
                )
        # Files existence (if provided)
        for label, path in (
            ("cert_file", s.cert_file),
            ("key_file", s.key_file),
            ("ca_cert_file", s.ca_cert_file),
            ("crl_file", s.crl_file),
        ):
            if path and not os.path.exists(path):
                e.append(ValidationError(f"server.{label} not found: {path}"))

        # Validate certificate validity if files exist
        if (
            s.cert_file
            and s.key_file
            and os.path.exists(s.cert_file)
            and os.path.exists(s.key_file)
        ):
            # Check certificate-key match
            if not CertificateValidator.validate_certificate_key_match(
                s.cert_file, s.key_file
            ):
                e.append(
                    ValidationError("server.cert_file does not match server.key_file")
                )
            # Check certificate expiry
            if not CertificateValidator.validate_certificate_not_expired(s.cert_file):
                e.append(ValidationError("server.cert_file is expired"))

            # Check CRL if specified
            if s.crl_file:
                if not os.path.exists(s.crl_file):
                    e.append(
                        ValidationError(f"server.crl_file not found: {s.crl_file}")
                    )
                elif not CertificateValidator.validate_certificate_not_revoked(
                    s.cert_file, s.crl_file
                ):
                    e.append(
                        ValidationError(
                            "server.cert_file is revoked according to server.crl_file"
                        )
                    )

        # Validate certificate chain - use CA cert if provided, otherwise use system store
        if s.cert_file and os.path.exists(s.cert_file):
            if s.ca_cert_file and os.path.exists(s.ca_cert_file):
                # Use provided CA certificate
                if not CertificateValidator.validate_certificate_chain(
                    s.cert_file, s.ca_cert_file
                ):
                    e.append(
                        ValidationError(
                            "server.cert_file is not signed by server.ca_cert_file"
                        )
                    )
            else:
                # Use system CA store (only for https, mtls requires CA)
                if s.protocol == "https":
                    if not CertificateValidator.validate_certificate_with_system_store(
                        s.cert_file
                    ):
                        e.append(
                            ValidationError(
                                "server.cert_file is not valid according to system CA store"
                            )
                        )

        return e

    def _validate_proxy_client(self, model: SimpleConfigModel) -> List[ValidationError]:
        """
        Validate proxy_client configuration.

        Note: Validation is performed only when enabled=True, because if the client
        is disabled, its configuration is not used. The registration.auto_on_startup
        flag controls automatic registration behavior but doesn't affect whether
        the client configuration needs to be valid.

        IMPORTANT: proxy_client.protocol indicates the SERVER's protocol, not the proxy's protocol.
        The proxy itself typically runs on HTTP (for test proxy) or may have its own protocol.
        Client certificates in proxy_client are used for connecting TO the proxy (if proxy uses HTTPS/mTLS),
        not for the server's own protocol. For test proxy (HTTP), these certificates are not used
        but may be validated for consistency.
        """
        e: List[ValidationError] = []
        pc = model.proxy_client
        if pc.enabled:
            if not pc.host:
                e.append(ValidationError("proxy_client.host is required when enabled"))
            if not isinstance(pc.port, int):  # type: ignore[unreachable]
                e.append(ValidationError("proxy_client.port must be integer"))
            if pc.protocol not in ("http", "https", "mtls"):
                e.append(
                    ValidationError(
                        "proxy_client.protocol must be one of: http, https, mtls"
                    )
                )
            # Validate server_id if provided (preferred field name)
            if pc.server_id is not None and not isinstance(pc.server_id, str):
                e.append(ValidationError("proxy_client.server_id must be a string"))
            if pc.server_id is not None and not pc.server_id.strip():
                e.append(ValidationError("proxy_client.server_id cannot be empty"))
            # Warn about deprecated server_name (but allow it for backward compatibility)
            if pc.server_name is not None and pc.server_id is None:
                # server_name is deprecated but allowed for backward compatibility
                # registration_context.py will use server_id if available, fallback to server_name
                pass
            # Protocol-specific certificate requirements
            # NOTE: These certificates are for connecting TO the proxy (if proxy uses HTTPS/mTLS),
            # not for the server's own protocol. For test proxy (HTTP), these are not used.
            if pc.protocol == "mtls":
                # For mtls: all certificates are required
                if not pc.cert_file:
                    e.append(
                        ValidationError(
                            "proxy_client.cert_file is required for mtls protocol"
                        )
                    )
                if not pc.key_file:
                    e.append(
                        ValidationError(
                            "proxy_client.key_file is required for mtls protocol"
                        )
                    )
                if not pc.ca_cert_file:
                    e.append(
                        ValidationError(
                            "proxy_client.ca_cert_file is required for mtls protocol"
                        )
                    )
            elif pc.protocol == "https":
                # For https: certificates are optional, but if one is specified, both must be
                if (pc.cert_file and not pc.key_file) or (
                    pc.key_file and not pc.cert_file
                ):
                    e.append(
                        ValidationError(
                            "proxy_client.cert_file and proxy_client.key_file must both be specified or both omitted for https"
                        )
                    )
            # Files existence (if provided)
            for label, path in (
                ("cert_file", pc.cert_file),
                ("key_file", pc.key_file),
                ("ca_cert_file", pc.ca_cert_file),
                ("crl_file", pc.crl_file),
            ):
                if path and not os.path.exists(path):
                    e.append(ValidationError(f"proxy_client.{label} not found: {path}"))

            # Validate certificate validity if files exist
            if (
                pc.cert_file
                and pc.key_file
                and os.path.exists(pc.cert_file)
                and os.path.exists(pc.key_file)
            ):
                # Check certificate-key match
                if not CertificateValidator.validate_certificate_key_match(
                    pc.cert_file, pc.key_file
                ):
                    e.append(
                        ValidationError(
                            "proxy_client.cert_file does not match proxy_client.key_file"
                        )
                    )
                # Check certificate expiry
                if not CertificateValidator.validate_certificate_not_expired(
                    pc.cert_file
                ):
                    e.append(ValidationError("proxy_client.cert_file is expired"))

                # Check CRL if specified
                if pc.crl_file:
                    if not os.path.exists(pc.crl_file):
                        e.append(
                            ValidationError(
                                f"proxy_client.crl_file not found: {pc.crl_file}"
                            )
                        )
                    elif not CertificateValidator.validate_certificate_not_revoked(
                        pc.cert_file, pc.crl_file
                    ):
                        e.append(
                            ValidationError(
                                "proxy_client.cert_file is revoked according to proxy_client.crl_file"
                            )
                        )

            # Validate certificate chain - use CA cert if provided, otherwise use system store
            # NOTE: These certificates are for connecting TO the proxy (if proxy uses HTTPS/mTLS),
            # not for the server's own protocol. For test proxy (HTTP), these are not used.
            if pc.cert_file and os.path.exists(pc.cert_file):
                if pc.ca_cert_file and os.path.exists(pc.ca_cert_file):
                    # Use provided CA certificate
                    if not CertificateValidator.validate_certificate_chain(
                        pc.cert_file, pc.ca_cert_file
                    ):
                        e.append(
                            ValidationError(
                                "proxy_client.cert_file is not signed by proxy_client.ca_cert_file"
                            )
                        )
                else:
                    # Use system CA store (only for https, mtls requires CA)
                    # NOTE: This validation is for proxy connection certificates, not server protocol
                    if pc.protocol == "https":
                        if not CertificateValidator.validate_certificate_with_system_store(
                            pc.cert_file
                        ):
                            e.append(
                                ValidationError(
                                    "proxy_client.cert_file is not valid according to system CA store"
                                )
                            )

            # Heartbeat
            if not pc.heartbeat.endpoint:
                e.append(ValidationError("proxy_client.heartbeat.endpoint is required"))
            if not isinstance(pc.heartbeat.interval, int) or pc.heartbeat.interval <= 0:
                e.append(
                    ValidationError(
                        "proxy_client.heartbeat.interval must be positive integer"
                    )
                )
            # Registration endpoints
            if not pc.registration.register_endpoint:
                e.append(
                    ValidationError(
                        "proxy_client.registration.register_endpoint is required"
                    )
                )
            if not pc.registration.unregister_endpoint:
                e.append(
                    ValidationError(
                        "proxy_client.registration.unregister_endpoint is required"
                    )
                )
        return e

    def _validate_auth(self, model: SimpleConfigModel) -> List[ValidationError]:
        e: List[ValidationError] = []
        a = model.auth
        if a.use_roles and not a.use_token:
            e.append(
                ValidationError("auth.use_roles requires auth.use_token to be true")
            )
        if a.use_token and not a.tokens:
            e.append(
                ValidationError(
                    "auth.tokens must be provided when auth.use_token is true"
                )
            )
        return e
