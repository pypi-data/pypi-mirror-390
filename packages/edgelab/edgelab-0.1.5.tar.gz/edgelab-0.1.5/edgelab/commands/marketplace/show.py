"""Marketplace show command."""

import sys
from rich.panel import Panel
from rich.table import Table
from rich import box

from edgelab.api.client import EdgeLabClient
from edgelab.api.exceptions import EdgeLabAPIError
from edgelab.config import get_settings
from edgelab.utils import console, print_error, print_info


def cmd_marketplace_show(strategy_id: str):
    """Show detailed strategy information.

    Args:
        strategy_id: Strategy ID or name
    """
    settings = get_settings()

    if not settings.is_authenticated():
        console.print()
        print_error("Not logged in")
        console.print()
        console.print("[dim]Please login first:[/dim]")
        console.print("  [cyan]edgelab auth login[/cyan]")
        console.print()
        sys.exit(1)

    client = EdgeLabClient()

    try:
        # Try to get strategy details
        # For now, just show a placeholder
        console.print()
        print_info(f"Strategy details for: {strategy_id}")
        console.print("[yellow]⚠️  Detailed view coming soon![/yellow]")
        console.print()

    except EdgeLabAPIError as e:
        print_error(f"API error: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to fetch strategy: {e}")
        sys.exit(1)

