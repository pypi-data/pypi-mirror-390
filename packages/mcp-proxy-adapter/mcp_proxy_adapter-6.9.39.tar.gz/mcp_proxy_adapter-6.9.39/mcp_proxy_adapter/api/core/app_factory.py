"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Application factory for MCP Proxy Adapter API.
"""

from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI, Body
from mcp_proxy_adapter.api.handlers import (
    handle_json_rpc,
    handle_batch_json_rpc,
    get_server_health,
    get_commands_list,
)

# from mcp_proxy_adapter.api.middleware import setup_middleware
try:
    from mcp_proxy_adapter.api.schemas import (
        JsonRpcRequest,
        JsonRpcSuccessResponse,
        JsonRpcErrorResponse,
        HealthResponse,
        CommandListResponse,
        APIToolDescription,
    )
except Exception:
    # If schemas are unavailable, define minimal type aliases to satisfy annotations
    JsonRpcRequest = Dict[str, Any]  # type: ignore
    JsonRpcSuccessResponse = Dict[str, Any]  # type: ignore
    JsonRpcErrorResponse = Dict[str, Any]  # type: ignore
    HealthResponse = Dict[str, Any]  # type: ignore
    CommandListResponse = Dict[str, Any]  # type: ignore
    APIToolDescription = Dict[str, Any]  # type: ignore

try:
    from mcp_proxy_adapter.api.tools import get_tool_description, execute_tool
except Exception:
    get_tool_description = None
    execute_tool = None
from mcp_proxy_adapter.core.logging import get_global_logger
from mcp_proxy_adapter.custom_openapi import custom_openapi_with_fallback
from .ssl_context_factory import SSLContextFactory
from .lifespan_manager import LifespanManager


class AppFactory:
    """Factory for creating FastAPI applications."""

    def __init__(self):
        """Initialize app factory."""
        self.logger = get_global_logger()
        self.ssl_factory = SSLContextFactory()
        self.lifespan_manager = LifespanManager()

    def create_app(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        version: Optional[str] = None,
        app_config: Optional[Dict[str, Any]] = None,
        config_path: Optional[str] = None,
    ) -> FastAPI:
        """
        Creates and configures FastAPI application.

        Args:
            title: Application title (default: "MCP Proxy Adapter")
            description: Application description (default: "JSON-RPC API for interacting with MCP Proxy")
            version: Application version (default: "1.0.0")
            app_config: Application configuration dictionary (optional)
            config_path: Path to configuration file (optional)

        Returns:
            Configured FastAPI application.

        Raises:
            SystemExit: If authentication is enabled but required files are missing (security issue)
        """
        # Use provided configuration or fallback to global config
        if app_config is not None:
            if hasattr(app_config, "get_all"):
                current_config = app_config.get_all()
            elif hasattr(app_config, "keys"):
                current_config = app_config
            else:
                # If app_config is not a dict-like object, use it as is
                current_config = app_config
        else:
            # If no app_config provided, try to get global config
            try:
                from mcp_proxy_adapter.config import get_config

                current_config = get_config().get_all()
            except Exception:
                # If global config is not available, create empty config
                current_config = {}

        # Debug: Check what config is passed to create_app
        if app_config:
            if hasattr(app_config, "keys"):
                print(
                    f"🔍 Debug: create_app received app_config keys: {list(app_config.keys())}"
                )
                # Debug SSL configuration
                protocol = app_config.get("server", {}).get("protocol", "http")
                verify_client = app_config.get("transport", {}).get(
                    "verify_client", False
                )
                ssl_enabled = protocol in ["https", "mtls"] or verify_client
                print(f"🔍 Debug: create_app SSL config: enabled={ssl_enabled}")
                print(f"🔍 Debug: create_app protocol: {protocol}")
                print(f"🔍 Debug: create_app verify_client: {verify_client}")
            else:
                print(
                    f"🔍 Debug: create_app received app_config type: {type(app_config)}"
                )
        else:
            print("🔍 Debug: create_app received no app_config, using global config")

        # Security check: Validate configuration strictly at startup (fail-fast)
        self._validate_configuration(current_config)

        # Security check: Validate all authentication configurations before startup
        self._validate_security_configuration(current_config)

        # Security check: Validate certificates at startup (fail-fast)
        self._validate_certificates(current_config)

        # Set default values
        title = title or "MCP Proxy Adapter"
        description = description or "JSON-RPC API for interacting with MCP Proxy"
        version = version or "1.0.0"

        # Create lifespan manager
        lifespan = self.lifespan_manager.create_lifespan(config_path, current_config)

        # Create FastAPI application
        app = FastAPI(
            title=title,
            description=description,
            version=version,
            lifespan=lifespan,
        )

        # Setup middleware - disabled for now
        # setup_middleware(app, current_config)

        # Setup routes
        self._setup_routes(app)

        # Setup OpenAPI
        app.openapi = lambda: custom_openapi_with_fallback(app)

        return app

    def _validate_configuration(self, current_config: Dict[str, Any]) -> None:
        """Validate configuration at startup."""
        try:
            from mcp_proxy_adapter.core.validation.config_validator import (
                ConfigValidator,
            )

            validator = ConfigValidator()
            validator.config_data = current_config
            validation_results = validator.validate_config()
            errors = [r for r in validation_results if r.level == "error"]
            warnings = [r for r in validation_results if r.level == "warning"]

            if errors:
                self.logger.critical(
                    "CRITICAL CONFIG ERROR: Invalid configuration at startup:"
                )
                for error in errors:
                    self.logger.critical(f"  - {error.message}")
                raise SystemExit(1)
            for warning in warnings:
                self.logger.warning(f"Config warning: {warning.message}")
        except Exception as ex:
            self.logger.error(f"Failed to run startup configuration validation: {ex}")

    def _validate_security_configuration(self, current_config: Dict[str, Any]) -> None:
        """Validate security configuration at startup."""
        security_errors = []

        print(f"🔍 Debug: current_config keys: {list(current_config.keys())}")
        if "security" in current_config:
            print(f"🔍 Debug: security config: {current_config['security']}")
        if "roles" in current_config:
            print(f"🔍 Debug: roles config: {current_config['roles']}")

        # Check security framework configuration only if enabled
        security_config = current_config.get("security", {})
        if security_config.get("enabled", False):
            # Validate security framework configuration
            from mcp_proxy_adapter.core.unified_config_adapter import (
                UnifiedConfigAdapter,
            )

            adapter = UnifiedConfigAdapter()
            validation_result = adapter.validate_configuration(current_config)

            if not validation_result.is_valid:
                security_errors.extend(validation_result.errors)

        # Check roles configuration only if enabled
        # Roles validation is handled by UnifiedConfigAdapter in security section validation
        # No need for separate validation here

        # Fail if there are security errors
        if security_errors:
            self.logger.critical(
                "CRITICAL SECURITY ERROR: Invalid security configuration at startup:"
            )
            for error in security_errors:
                self.logger.critical(f"  - {error}")
            raise SystemExit(1)

    def _validate_certificates(self, current_config: Dict[str, Any]) -> None:
        """
        Validate certificates at startup.

        Checks:
        - Certificate-key match
        - Certificate expiry
        - Certificate chain (with provided CA or system CA store)

        Raises SystemExit(1) if validation fails.
        """
        try:
            from mcp_proxy_adapter.core.certificate.certificate_validator import (
                CertificateValidator,
            )
            import os

            certificate_errors = []

            # Check if this is SimpleConfig format
            if "server" in current_config and "proxy_client" in current_config:
                # SimpleConfig format
                from mcp_proxy_adapter.core.config.simple_config import (
                    SimpleConfigModel,
                    ServerConfig,
                    ProxyClientConfig,
                    AuthConfig,
                )
                from mcp_proxy_adapter.core.config.simple_config_validator import (
                    SimpleConfigValidator,
                )

                try:
                    # Try to load as SimpleConfig
                    server_config = current_config.get("server", {})
                    proxy_client_config = current_config.get("proxy_client", {})
                    auth_config = current_config.get("auth", {})

                    server = ServerConfig(**server_config)  # type: ignore[arg-type]
                    proxy_client = ProxyClientConfig(**proxy_client_config)  # type: ignore[arg-type]
                    auth = AuthConfig(**auth_config)  # type: ignore[arg-type]

                    # Handle nested structures
                    if isinstance(proxy_client_config.get("heartbeat"), dict):
                        from mcp_proxy_adapter.core.config.simple_config import (
                            HeartbeatConfig,
                        )

                        proxy_client.heartbeat = HeartbeatConfig(
                            **proxy_client_config["heartbeat"]
                        )  # type: ignore[arg-type]
                    if isinstance(proxy_client_config.get("registration"), dict):
                        from mcp_proxy_adapter.core.config.simple_config import (
                            RegistrationConfig,
                        )

                        proxy_client.registration = RegistrationConfig(
                            **proxy_client_config["registration"]
                        )  # type: ignore[arg-type]

                    model = SimpleConfigModel(
                        server=server, proxy_client=proxy_client, auth=auth
                    )
                    validator = SimpleConfigValidator()
                    validation_errors = validator.validate(model)

                    if validation_errors:
                        for error in validation_errors:
                            certificate_errors.append(error.message)

                except Exception as e:
                    self.logger.error(
                        f"Failed to validate as SimpleConfig format: {e}"
                    )
                    certificate_errors.append(
                        f"Configuration validation failed: {e}. Only SimpleConfig format is supported."
                    )

            # Fail if there are certificate errors
            if certificate_errors:
                self.logger.critical(
                    "CRITICAL CERTIFICATE ERROR: Certificate validation failed at startup:"
                )
                for error in certificate_errors:
                    self.logger.critical(f"  - {error}")
                self.logger.critical(
                    "Server startup aborted due to certificate validation errors"
                )
                raise SystemExit(1)

        except SystemExit:
            raise
        except Exception as ex:
            self.logger.error(f"Failed to run certificate validation: {ex}")
            # Don't fail startup if validation itself fails, but log the error
            self.logger.warning(
                "Certificate validation could not be completed, but server will continue to start"
            )

    def _setup_routes(self, app: FastAPI) -> None:
        """Setup application routes."""

        @app.get("/health", response_model=HealthResponse)
        async def health():  # type: ignore
            return await get_server_health()  # type: ignore[misc]

        @app.get("/commands", response_model=CommandListResponse)
        async def commands():  # type: ignore
            return await get_commands_list()  # type: ignore[misc]

        @app.post(
            "/api/jsonrpc",
            response_model=Union[JsonRpcSuccessResponse, JsonRpcErrorResponse],
        )
        async def jsonrpc(request: JsonRpcRequest):  # type: ignore
            return await handle_json_rpc(request.dict())  # type: ignore[misc]

        @app.post(
            "/api/jsonrpc/batch",
            response_model=List[Union[JsonRpcSuccessResponse, JsonRpcErrorResponse]],
        )
        async def jsonrpc_batch(requests: List[JsonRpcRequest]):  # type: ignore
            return await handle_batch_json_rpc([req.dict() for req in requests])  # type: ignore[misc]

        # Optional tool endpoints if tools module is available
        if get_tool_description and execute_tool:

            @app.get("/api/tools", response_model=List[APIToolDescription])
            async def tools():  # type: ignore
                return await get_tool_description()  # type: ignore[misc]

            @app.post("/api/tools/{tool_name}")
            async def execute_tool_endpoint(
                tool_name: str, params: Dict[str, Any] = Body(...)
            ):
                return await execute_tool(tool_name, params)  # type: ignore[misc]
