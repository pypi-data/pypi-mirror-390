"""Marketplace list command."""

import sys
from rich.table import Table
from rich import box

from edgelab.api.client import EdgeLabClient
from edgelab.api.exceptions import EdgeLabAPIError
from edgelab.config import get_settings
from edgelab.utils import console, print_error, print_info


def cmd_marketplace_list(
    sort: str = "sharpe",
    tags: str = None,
    min_sharpe: float = None,
    max_drawdown: float = None,
):
    """List public strategies in marketplace.

    Args:
        sort: Sort order (sharpe, return, clones, recent)
        tags: Comma-separated tags to filter by
        min_sharpe: Minimum Sharpe ratio filter
        max_drawdown: Maximum drawdown filter
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
        params = {"sort": sort, "limit": 50}
        if tags:
            params["tags"] = tags.split(",")
        if min_sharpe is not None:
            params["min_sharpe"] = min_sharpe
        if max_drawdown is not None:
            params["max_drawdown"] = max_drawdown

        response = client.get("/api/v1/edgelab/marketplace/strategies", authenticated=True, params=params)
        strategies = response.get("data", [])

        if not strategies:
            console.print()
            print_info("No strategies found matching your criteria.")
            console.print()
            return

        # Create table
        table = Table(
            title="[bold cyan]Public Strategies Marketplace[/bold cyan]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold yellow",
        )

        table.add_column("Name", style="cyan", width=25)
        table.add_column("Version", style="white", width=8)
        table.add_column("Sharpe", justify="right", style="green", width=8)
        table.add_column("Return", justify="right", style="green", width=10)
        table.add_column("Max DD", justify="right", style="red", width=8)
        table.add_column("Trades", justify="right", style="white", width=8)
        table.add_column("Clones", justify="right", style="dim", width=8)

        for strategy in strategies:
            perf = strategy.get("performance", {})
            sharpe = perf.get("sharpe_ratio")
            total_return = perf.get("total_return")
            max_dd = perf.get("max_drawdown")
            trades = perf.get("total_trades")

            sharpe_str = f"{sharpe:.2f}" if sharpe else "N/A"
            return_str = f"{total_return*100:.1f}%" if total_return else "N/A"
            dd_str = f"{max_dd*100:.1f}%" if max_dd else "N/A"
            trades_str = str(trades) if trades else "0"

            table.add_row(
                strategy.get("name", "Unknown"),
                strategy.get("version", "v1"),
                sharpe_str,
                return_str,
                dd_str,
                trades_str,
                str(strategy.get("clone_count", 0)),
            )

        console.print()
        console.print(table)
        console.print()

    except EdgeLabAPIError as e:
        print_error(f"API error: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to fetch strategies: {e}")
        sys.exit(1)

