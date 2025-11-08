"""
Custom Echo Command
This module demonstrates a custom command implementation for the full application example.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from mcp_proxy_adapter.commands.base import BaseCommand
from mcp_proxy_adapter.commands.result import CommandResult


class CustomEchoResult(CommandResult):
    """Result class for custom echo command."""

    def __init__(self, message: str, timestamp: str, echo_count: int):
        self.message = message
        self.timestamp = timestamp
        self.echo_count = echo_count




class CustomEchoCommand(BaseCommand):
    """Custom echo command implementation."""

    def __init__(self):
        super().__init__()
        self.echo_count = 0




    async def execute(self, params: Dict[str, Any]) -> CustomEchoResult:
        """Execute the custom echo command."""
        message = params.get("message", "Hello from custom echo!")
        repeat = min(max(params.get("repeat", 1), 1), 10)
        self.echo_count += 1
        from datetime import datetime

        timestamp = datetime.now().isoformat()
        # Repeat the message
        echoed_message = " ".join([message] * repeat)
        return CustomEchoResult(
            message=echoed_message, timestamp=timestamp, echo_count=self.echo_count
        )
