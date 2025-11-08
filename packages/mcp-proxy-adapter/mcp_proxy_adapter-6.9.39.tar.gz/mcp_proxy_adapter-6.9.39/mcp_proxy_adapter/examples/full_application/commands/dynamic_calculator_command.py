"""
Dynamic Calculator Command
This module demonstrates a dynamically loaded command implementation for the full application example.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from mcp_proxy_adapter.commands.base import BaseCommand
from mcp_proxy_adapter.commands.result import CommandResult


class CalculatorResult(CommandResult):
    """Result class for calculator command."""

    def __init__(self, operation: str, result: float, expression: str):
        self.operation = operation
        self.result = result
        self.expression = expression




class DynamicCalculatorCommand(BaseCommand):
    """Dynamic calculator command implementation."""




    async def execute(self, params: Dict[str, Any]) -> CalculatorResult:
        """Execute the calculator command."""
        operation = params.get("operation")
        a = params.get("a")
        b = params.get("b")
        if operation == "add":
            result = a + b
            expression = f"{a} + {b}"
        elif operation == "subtract":
            result = a - b
            expression = f"{a} - {b}"
        elif operation == "multiply":
            result = a * b
            expression = f"{a} * {b}"
        elif operation == "divide":
            if b == 0:
                raise ValueError("Division by zero is not allowed")
            result = a / b
            expression = f"{a} / {b}"
        else:
            raise ValueError(f"Unknown operation: {operation}")
        return CalculatorResult(
            operation=operation, result=result, expression=expression
        )
