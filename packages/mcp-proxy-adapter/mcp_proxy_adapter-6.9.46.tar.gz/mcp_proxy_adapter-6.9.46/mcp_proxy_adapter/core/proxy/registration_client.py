"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Registration client for proxy registration.
"""

from typing import Dict, Any
import aiohttp

from mcp_proxy_adapter.core.logging import get_global_logger
from .auth_manager import AuthManager
from .ssl_manager import SSLManager


class RegistrationClient:
    """Client for proxy registration operations."""

    def __init__(
        self,
        client_security,
        registration_config: Dict[str, Any],
        config: Dict[str, Any],
        proxy_url: str,
    ):
        """
        Initialize registration client.

        Args:
            client_security: Client security manager instance
            registration_config: Registration configuration
            config: Application configuration
            proxy_url: Proxy server URL
        """
        self.client_security = client_security
        self.registration_config = registration_config
        self.config = config
        self.proxy_url = proxy_url
        self.logger = get_global_logger()
        
        # Initialize managers
        self.auth_manager = AuthManager(client_security, registration_config)
        self.ssl_manager = SSLManager(
            client_security, registration_config, config, proxy_url
        )

    def _prepare_registration_data(self, server_url: str) -> Dict[str, Any]:
        """
        Prepare registration data.

        Args:
            server_url: Server URL to register

        Returns:
            Registration data dictionary
        """
        # Proxy expects "name" field, use server_id or server_name
        server_name = (
            self.registration_config.get("server_id")
            or self.registration_config.get("server_name")
            or "mcp_proxy_adapter"
        )
        
        return {
            "name": server_name,
            "url": server_url,
            "capabilities": self.registration_config.get("capabilities", ["jsonrpc"]),
            "metadata": {
                "server_id": self.registration_config.get("server_id"),
                "server_name": self.registration_config.get("server_name"),
                "description": self.registration_config.get("description", ""),
                "version": self.registration_config.get("version", "1.0.0"),
            },
        }

    async def register(self, server_url: str) -> bool:
        """
        Register server with proxy.

        Args:
            server_url: Server URL to register

        Returns:
            True if registration successful, False otherwise
        """
        try:
            registration_data = self._prepare_registration_data(server_url)
            
            # Get SSL context if needed
            ssl_context = self.ssl_manager.get_ssl_context()
            
            # Get headers with authentication if needed
            headers = self.auth_manager.get_headers()
            
            # Prepare request configuration
            connector = None
            if ssl_context:
                connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            # Send registration request
            async with aiohttp.ClientSession(connector=connector) as session:
                register_url = f"{self.proxy_url}/register"
                self.logger.info(f"Attempting to register server with proxy at {register_url}")
                self.logger.debug(f"Registration data: {registration_data}")
                self.logger.debug(f"Headers: {headers}")
                
                # Ensure Content-Type header is set
                if "Content-Type" not in headers:
                    headers["Content-Type"] = "application/json"
                
                async with session.post(
                    register_url,
                    json=registration_data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.logger.info(f"✅ Successfully registered with proxy. Server key: {result.get('key')}")
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.error(
                            f"❌ Failed to register with proxy: {response.status} {response.reason}: {error_text}"
                        )
                        return False
                        
        except Exception as e:
            self.logger.error(f"Registration error: {e}", exc_info=True)
            return False

    async def unregister(self) -> bool:
        """
        Unregister server from proxy.

        Returns:
            True if unregistration successful, False otherwise
        """
        try:
            server_name = (
                self.registration_config.get("server_id")
                or self.registration_config.get("server_name")
                or "mcp_proxy_adapter"
            )
            
            unregister_data = {
                "name": server_name,
                "url": "",  # Not needed for unregister
                "capabilities": [],
                "metadata": {},
            }
            
            # Get SSL context if needed
            ssl_context = self.ssl_manager.get_ssl_context()
            
            # Get headers with authentication if needed
            headers = self.auth_manager.get_headers()
            
            # Prepare request configuration
            connector = None
            if ssl_context:
                connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            # Send unregistration request
            async with aiohttp.ClientSession(connector=connector) as session:
                unregister_url = f"{self.proxy_url}/unregister"
                
                async with session.post(
                    unregister_url,
                    json=unregister_data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        self.logger.info("✅ Successfully unregistered from proxy")
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.warning(
                            f"⚠️ Failed to unregister from proxy: {response.status} {response.reason}: {error_text}"
                        )
                        return False
                        
        except Exception as e:
            self.logger.error(f"Unregistration error: {e}", exc_info=True)
            return False
