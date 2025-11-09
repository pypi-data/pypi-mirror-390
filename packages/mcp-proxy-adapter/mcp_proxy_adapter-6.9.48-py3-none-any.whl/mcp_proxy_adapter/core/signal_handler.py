"""
Signal handler for graceful shutdown with proxy unregistration.

This module provides signal handling for SIGTERM, SIGINT, and SIGHUP
to ensure proper proxy unregistration before server shutdown.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import signal
import threading
from typing import Optional, Callable, Any
from mcp_proxy_adapter.core.logging import get_global_logger


class SignalHandler:
    """
    Signal handler for graceful shutdown with proxy unregistration.
    """
    
    def __init__(self):
        """Initialize signal handler."""
        self._shutdown_callback: Optional[Callable] = None
        self._shutdown_event = threading.Event()
        self._original_handlers = {}
        self._setup_signal_handlers()
    
    def set_shutdown_callback(self, callback: Callable):
        """
        Set callback function to be called during shutdown.
        
        Args:
            callback: Function to call during shutdown
        """
        self._shutdown_callback = callback
        get_global_logger().info("Shutdown callback set for signal handler")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        # Handle SIGTERM (termination signal)
        self._original_handlers[signal.SIGTERM] = signal.signal(
            signal.SIGTERM, self._handle_shutdown_signal
        )
        
        # Handle SIGINT (Ctrl+C)
        self._original_handlers[signal.SIGINT] = signal.signal(
            signal.SIGINT, self._handle_shutdown_signal
        )
        
        # Handle SIGHUP (hangup signal)
        self._original_handlers[signal.SIGHUP] = signal.signal(
            signal.SIGHUP, self._handle_shutdown_signal
        )
        
        get_global_logger().info("Signal handlers installed for SIGTERM, SIGINT, SIGHUP")
    
    
    
    def wait_for_shutdown(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for shutdown signal.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if shutdown signal received, False if timeout
        """
        return self._shutdown_event.wait(timeout)
    
    def is_shutdown_requested(self) -> bool:
        """
        Check if shutdown has been requested.
        
        Returns:
            True if shutdown signal received
        """
        return self._shutdown_event.is_set()
    


# Global signal handler instance
_signal_handler: Optional[SignalHandler] = None


def get_signal_handler() -> SignalHandler:
    """Get the global signal handler instance."""
    global _signal_handler
    if _signal_handler is None:
        _signal_handler = SignalHandler()
    return _signal_handler






def is_shutdown_requested() -> bool:
    """
    Check if shutdown has been requested.
    
    Returns:
        True if shutdown signal received
    """
    handler = get_signal_handler()
    return handler.is_shutdown_requested()
