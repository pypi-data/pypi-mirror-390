"""Rich console utilities for beautiful terminal output."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# Global console instance
console = Console()


def print_success(message: str):
    """Print success message with checkmark."""
    console.print(f"✓ {message}", style="bold green")


def print_error(message: str):
    """Print error message with X."""
    console.print(f"✗ {message}", style="bold red")


def print_warning(message: str):
    """Print warning message."""
    console.print(f"⚠️  {message}", style="bold yellow")


def print_info(message: str):
    """Print info message."""
    console.print(f"ℹ️  {message}", style="bold cyan")
