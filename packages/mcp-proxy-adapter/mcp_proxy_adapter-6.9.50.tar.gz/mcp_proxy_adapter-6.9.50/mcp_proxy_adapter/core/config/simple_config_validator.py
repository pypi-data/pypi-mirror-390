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
        errors.extend(self._validate_client(model))
        errors.extend(self._validate_registration(model))
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
            # For mtls: cert_file and key_file are required
            # CA is required if use_system_ca=False (default), optional if use_system_ca=True
            if not s.cert_file:
                e.append(
                    ValidationError("server.cert_file is required for mtls protocol")
                )
            if not s.key_file:
                e.append(
                    ValidationError("server.key_file is required for mtls protocol")
                )
            # CA validation is handled below based on use_system_ca flag
        elif s.protocol == "https":
            # For https: certificates are optional, but if one is specified, both must be
            # If key is specified but cert is not - this is an error
            if s.key_file and not s.cert_file:
                e.append(
                    ValidationError(
                        "server.key_file is specified but server.cert_file is missing for https protocol"
                    )
                )
            if s.cert_file and not s.key_file:
                e.append(
                    ValidationError(
                        "server.cert_file is specified but server.key_file is missing for https protocol"
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

            # Validate CRL if specified
            if s.crl_file:
                crl_valid, crl_error = CertificateValidator.validate_crl_file(s.crl_file)
                if not crl_valid:
                    e.append(
                        ValidationError(f"server.crl_file validation failed: {crl_error}")
                    )
                else:
                    # Check if certificate is revoked according to CRL
                    if not CertificateValidator.validate_certificate_not_revoked(
                        s.cert_file, s.crl_file
                    ):
                        e.append(
                            ValidationError(
                                "server.cert_file is revoked according to server.crl_file"
                            )
                        )

        # Validate certificate chain - use CA cert if provided, otherwise check use_system_ca
        if s.cert_file and os.path.exists(s.cert_file):
            if s.ca_cert_file and os.path.exists(s.ca_cert_file):
                # Use provided CA certificate (only CA from config is used by default)
                if not CertificateValidator.validate_certificate_chain(
                    s.cert_file, s.ca_cert_file
                ):
                    e.append(
                        ValidationError(
                            "server.cert_file is not signed by server.ca_cert_file"
                        )
                    )
            else:
                # CA not provided - check if system CA is allowed
                if s.protocol == "mtls":
                    # For mTLS: CA is required if use_system_ca=False (default)
                    if s.use_system_ca:
                        # System CA is explicitly allowed
                        if not CertificateValidator.validate_certificate_with_system_store(
                            s.cert_file
                        ):
                            e.append(
                                ValidationError(
                                    "server.cert_file is not valid according to system CA store"
                                )
                            )
                    else:
                        # System CA is not allowed (default) - CA must be provided for mTLS
                        e.append(
                            ValidationError(
                                "server.ca_cert_file is required for mtls protocol when use_system_ca is False"
                            )
                        )
                elif s.protocol == "https":
                    # For HTTPS: CA is optional, but if not provided, use system CA if allowed
                    if s.use_system_ca:
                        # System CA is explicitly allowed
                        if not CertificateValidator.validate_certificate_with_system_store(
                            s.cert_file
                        ):
                            e.append(
                                ValidationError(
                                    "server.cert_file is not valid according to system CA store"
                                )
                            )
                    # If use_system_ca=False and CA not provided for HTTPS, that's OK
                    # (HTTPS can work without explicit CA validation)

        return e

    def _validate_client(self, model: SimpleConfigModel) -> List[ValidationError]:
        """
        Validate client configuration (for connecting to external servers).
        """
        e: List[ValidationError] = []
        c = model.client
        if c.enabled:
            if c.protocol not in ("http", "https", "mtls"):
                e.append(
                    ValidationError(
                        "client.protocol must be one of: http, https, mtls"
                    )
                )
            # Protocol-specific certificate requirements
            if c.protocol == "mtls":
                if not c.cert_file:
                    e.append(
                        ValidationError(
                            "client.cert_file is required for mtls protocol when enabled"
                        )
                    )
                if not c.key_file:
                    e.append(
                        ValidationError(
                            "client.key_file is required for mtls protocol when enabled"
                        )
                    )
            elif c.protocol == "https":
                if c.key_file and not c.cert_file:
                    e.append(
                        ValidationError(
                            "client.key_file is specified but client.cert_file is missing for https protocol"
                        )
                    )
                if c.cert_file and not c.key_file:
                    e.append(
                        ValidationError(
                            "client.cert_file is specified but client.key_file is missing for https protocol"
                        )
                    )
            # Files existence (if provided)
            for label, path in (
                ("cert_file", c.cert_file),
                ("key_file", c.key_file),
                ("ca_cert_file", c.ca_cert_file),
                ("crl_file", c.crl_file),
            ):
                if path and not os.path.exists(path):
                    e.append(ValidationError(f"client.{label} not found: {path}"))

            # Validate certificate validity if files exist
            if (
                c.cert_file
                and c.key_file
                and os.path.exists(c.cert_file)
                and os.path.exists(c.key_file)
            ):
                # Check certificate-key match
                if not CertificateValidator.validate_certificate_key_match(
                    c.cert_file, c.key_file
                ):
                    e.append(
                        ValidationError(
                            "client.cert_file does not match client.key_file"
                        )
                    )
                # Check certificate expiry
                if not CertificateValidator.validate_certificate_not_expired(c.cert_file):
                    e.append(ValidationError("client.cert_file is expired"))

                # Validate CRL if specified
                if c.crl_file:
                    crl_valid, crl_error = CertificateValidator.validate_crl_file(c.crl_file)
                    if not crl_valid:
                        e.append(
                            ValidationError(f"client.crl_file validation failed: {crl_error}")
                        )
                    else:
                        # Check if certificate is revoked according to CRL
                        if not CertificateValidator.validate_certificate_not_revoked(
                            c.cert_file, c.crl_file
                        ):
                            e.append(
                                ValidationError(
                                    "client.cert_file is revoked according to client.crl_file"
                                )
                            )

            # Validate certificate chain
            if c.cert_file and os.path.exists(c.cert_file):
                if c.ca_cert_file and os.path.exists(c.ca_cert_file):
                    if not CertificateValidator.validate_certificate_chain(
                        c.cert_file, c.ca_cert_file
                    ):
                        e.append(
                            ValidationError(
                                "client.cert_file is not signed by client.ca_cert_file"
                            )
                        )
                else:
                    if c.protocol == "mtls":
                        if c.use_system_ca:
                            if not CertificateValidator.validate_certificate_with_system_store(
                                c.cert_file
                            ):
                                e.append(
                                    ValidationError(
                                        "client.cert_file is not valid according to system CA store"
                                    )
                                )
                        else:
                            e.append(
                                ValidationError(
                                    "client.ca_cert_file is required for mtls protocol when use_system_ca is False"
                                )
                            )
                    elif c.protocol == "https":
                        if c.use_system_ca:
                            if not CertificateValidator.validate_certificate_with_system_store(
                                c.cert_file
                            ):
                                e.append(
                                    ValidationError(
                                        "client.cert_file is not valid according to system CA store"
                                    )
                                )
        return e

    def _validate_registration(self, model: SimpleConfigModel) -> List[ValidationError]:
        """
        Validate registration configuration (for registering with proxy server).
        """
        e: List[ValidationError] = []
        r = model.registration
        if r.enabled:
            if not r.host:
                e.append(ValidationError("registration.host is required when enabled"))
            if not isinstance(r.port, int):  # type: ignore[unreachable]
                e.append(ValidationError("registration.port must be integer"))
            if r.protocol not in ("http", "https", "mtls"):
                e.append(
                    ValidationError(
                        "registration.protocol must be one of: http, https, mtls"
                    )
                )
            # Validate server_id if provided
            if r.server_id is not None and not isinstance(r.server_id, str):
                e.append(ValidationError("registration.server_id must be a string"))
            if r.server_id is not None and not r.server_id.strip():
                e.append(ValidationError("registration.server_id cannot be empty"))
            # Protocol-specific certificate requirements
            if r.protocol == "mtls":
                if not r.cert_file:
                    e.append(
                        ValidationError(
                            "registration.cert_file is required for mtls protocol when enabled"
                        )
                    )
                if not r.key_file:
                    e.append(
                        ValidationError(
                            "registration.key_file is required for mtls protocol when enabled"
                        )
                    )
            elif r.protocol == "https":
                if r.key_file and not r.cert_file:
                    e.append(
                        ValidationError(
                            "registration.key_file is specified but registration.cert_file is missing for https protocol"
                        )
                    )
                if r.cert_file and not r.key_file:
                    e.append(
                        ValidationError(
                            "registration.cert_file is specified but registration.key_file is missing for https protocol"
                        )
                    )
            # Files existence (if provided)
            for label, path in (
                ("cert_file", r.cert_file),
                ("key_file", r.key_file),
                ("ca_cert_file", r.ca_cert_file),
                ("crl_file", r.crl_file),
            ):
                if path and not os.path.exists(path):
                    e.append(ValidationError(f"registration.{label} not found: {path}"))

            # Validate certificate validity if files exist
            if (
                r.cert_file
                and r.key_file
                and os.path.exists(r.cert_file)
                and os.path.exists(r.key_file)
            ):
                # Check certificate-key match
                if not CertificateValidator.validate_certificate_key_match(
                    r.cert_file, r.key_file
                ):
                    e.append(
                        ValidationError(
                            "registration.cert_file does not match registration.key_file"
                        )
                    )
                # Check certificate expiry
                if not CertificateValidator.validate_certificate_not_expired(r.cert_file):
                    e.append(ValidationError("registration.cert_file is expired"))

                # Validate CRL if specified
                if r.crl_file:
                    crl_valid, crl_error = CertificateValidator.validate_crl_file(r.crl_file)
                    if not crl_valid:
                        e.append(
                            ValidationError(f"registration.crl_file validation failed: {crl_error}")
                        )
                    else:
                        # Check if certificate is revoked according to CRL
                        if not CertificateValidator.validate_certificate_not_revoked(
                            r.cert_file, r.crl_file
                        ):
                            e.append(
                                ValidationError(
                                    "registration.cert_file is revoked according to registration.crl_file"
                                )
                            )

            # Validate certificate chain
            if r.cert_file and os.path.exists(r.cert_file):
                if r.ca_cert_file and os.path.exists(r.ca_cert_file):
                    if not CertificateValidator.validate_certificate_chain(
                        r.cert_file, r.ca_cert_file
                    ):
                        e.append(
                            ValidationError(
                                "registration.cert_file is not signed by registration.ca_cert_file"
                            )
                        )
                else:
                    if r.protocol == "mtls":
                        if r.use_system_ca:
                            if not CertificateValidator.validate_certificate_with_system_store(
                                r.cert_file
                            ):
                                e.append(
                                    ValidationError(
                                        "registration.cert_file is not valid according to system CA store"
                                    )
                                )
                        else:
                            e.append(
                                ValidationError(
                                    "registration.ca_cert_file is required for mtls protocol when use_system_ca is False"
                                )
                            )
                    elif r.protocol == "https":
                        if r.use_system_ca:
                            if not CertificateValidator.validate_certificate_with_system_store(
                                r.cert_file
                            ):
                                e.append(
                                    ValidationError(
                                        "registration.cert_file is not valid according to system CA store"
                                    )
                                )

            # Heartbeat
            if not r.heartbeat.endpoint:
                e.append(ValidationError("registration.heartbeat.endpoint is required"))
            if not isinstance(r.heartbeat.interval, int) or r.heartbeat.interval <= 0:
                e.append(
                    ValidationError(
                        "registration.heartbeat.interval must be positive integer"
                    )
                )
            # Registration endpoints
            if not r.register_endpoint:
                e.append(
                    ValidationError("registration.register_endpoint is required")
                )
            if not r.unregister_endpoint:
                e.append(
                    ValidationError("registration.unregister_endpoint is required")
                )
        return e

    def _validate_proxy_client(self, model: SimpleConfigModel) -> List[ValidationError]:
        """
        DEPRECATED: This method is kept for backward compatibility.
        Use _validate_registration instead.
        """
        # This method is no longer used but kept for compatibility
        return []

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
