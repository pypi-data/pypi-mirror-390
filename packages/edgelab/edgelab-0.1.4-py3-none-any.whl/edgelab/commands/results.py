"""Results display commands."""

import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

from edgelab.api.client import EdgeLabClient
from edgelab.api.exceptions import EdgeLabAPIError, UnauthorizedError, NotFoundError
from edgelab.config import get_settings
from edgelab.utils import console, print_success, print_error, print_warning, print_info
from rich.table import Table
from rich.panel import Panel
from rich import box


def cmd_results_show(workflow_id: str, show_detail: bool = False):
    """Show detailed results for a workflow.

    Args:
        workflow_id: Workflow UUID
        show_detail: If True, show detailed trade-by-trade breakdown
    """
    settings = get_settings()

    # Check authentication
    if not settings.is_authenticated():
        console.print()
        print_error("Not logged in")
        console.print()
        console.print("[dim]Please login first:[/dim]")
        console.print("  [cyan]edgelab auth login[/cyan]")
        console.print()
        sys.exit(1)

    try:
        # Fetch workflow from API
        client = EdgeLabClient()
        response = client.get(
            f"/api/v1/edgelab/workflows/{workflow_id}",
            authenticated=True,
        )

        # API wraps response in "data" field
        workflow = response.get("data", response)

        # Check status
        status = workflow.get("status")
        if status == "pending" or status == "processing":
            console.print()
            print_warning(f"Workflow is still {status}")
            console.print()
            console.print(f"[dim]Progress: {workflow.get('progress', 0)}%[/dim]")
            console.print()
            sys.exit(0)

        if status == "failed":
            console.print()
            print_error("Analysis failed")
            error_msg = workflow.get("error", "Unknown error")
            console.print(f"[red]{error_msg}[/red]")
            console.print()
            sys.exit(1)

        if status != "completed":
            console.print()
            print_warning(f"Unexpected status: {status}")
            console.print()
            sys.exit(1)

        # Display results
        display_results(workflow, show_detail=show_detail)

    except NotFoundError:
        console.print()
        print_error(f"Workflow not found: {workflow_id}")
        console.print()
        sys.exit(1)
    except UnauthorizedError:
        console.print()
        print_error("Unauthorized - please login again")
        console.print()
        console.print("[dim]Login:[/dim] [cyan]edgelab auth login[/cyan]")
        console.print()
        sys.exit(1)
    except EdgeLabAPIError as e:
        console.print()
        print_error(f"API error: {e}")
        console.print()
        sys.exit(1)
    except Exception as e:
        console.print()
        print_error(f"Failed to fetch results: {e}")
        console.print()
        sys.exit(1)


def display_results(workflow_data: Dict[str, Any], show_detail: bool = False):
    """Display analysis results in rich format.

    Args:
        workflow_data: Workflow data from API
        show_detail: If True, show detailed trade-by-trade breakdown
    """
    metadata = workflow_data.get("metadata")
    if not metadata:
        print_warning("No results data available")
        return

    # Parse metadata JSON if it's a string
    if isinstance(metadata, str):
        try:
            metadata = json.loads(metadata)
        except json.JSONDecodeError:
            print_error("Invalid metadata format")
            return

    # Extract results
    results = metadata.get("results", {})
    if not results:
        print_warning("No results found in metadata")
        return

    console.print()
    console.print(Panel.fit("[bold cyan]📊 Analysis Results[/bold cyan]", border_style="cyan"))
    console.print()

    # Display results for each symbol
    for symbol, symbol_results in results.items():
        display_symbol_results(symbol, symbol_results, show_detail=show_detail)

    # Display workflow info
    console.print()
    console.print(f"[dim]Workflow ID:[/dim] {workflow_data.get('workflow_id')}")
    console.print(f"[dim]Status:[/dim] {workflow_data.get('status')}")
    console.print()


def display_symbol_results(symbol: str, symbol_results: Dict[str, Any], show_detail: bool = False):
    """Display results for a single symbol.

    Args:
        symbol: Symbol name
        symbol_results: Results dict for this symbol
        show_detail: If True, show detailed trade-by-trade breakdown
    """
    console.print(f"[bold yellow]📈 Symbol: {symbol}[/bold yellow]")
    console.print()

    # Backtest results
    if "backtest" in symbol_results:
        display_backtest_results(symbol_results["backtest"], show_detail=show_detail)

    # Walkforward results
    if "walkforward" in symbol_results:
        display_walkforward_results(symbol_results["walkforward"], show_detail=show_detail)

    # Monte Carlo results
    if "montecarlo" in symbol_results:
        display_montecarlo_results(symbol_results["montecarlo"])

    # Stress test results
    if "stress" in symbol_results:
        display_stress_results(symbol_results["stress"], show_detail=show_detail)

    console.print()


def display_backtest_results(backtest: Dict[str, Any], show_detail: bool = False):
    """Display backtest results.

    Args:
        backtest: Backtest results dict
        show_detail: If True, show detailed trade-by-trade breakdown
    """
    metrics = backtest.get("metrics", {})
    trades = backtest.get("trades", [])

    table = Table(
        title="[bold cyan]Backtest[/bold cyan]",
        box=box.ROUNDED,
        show_header=False,
        padding=(0, 2),
    )
    table.add_column("Metric", style="bold yellow", width=25)
    table.add_column("Value", style="white")

    # Core metrics
    if "total_trades" in metrics:
        table.add_row("Total Trades", str(metrics["total_trades"]))
    if "win_rate" in metrics:
        table.add_row("Win Rate", f"{metrics['win_rate']:.1%}")
    if "total_pnl" in metrics:
        pnl = metrics["total_pnl"]
        color = "green" if pnl >= 0 else "red"
        table.add_row("Total P&L", f"[{color}]{pnl:,.2f}[/{color}]")
    if "sharpe_ratio" in metrics:
        table.add_row("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
    if "max_drawdown" in metrics:
        table.add_row("Max Drawdown", f"{metrics['max_drawdown']:.1%}")
    if "profit_factor" in metrics:
        table.add_row("Profit Factor", f"{metrics['profit_factor']:.2f}")
    if "avg_win" in metrics:
        table.add_row("Avg Win", f"{metrics['avg_win']:,.2f}")
    if "avg_loss" in metrics:
        table.add_row("Avg Loss", f"{metrics['avg_loss']:,.2f}")
    if "max_consecutive_wins" in metrics:
        table.add_row("Max Consecutive Wins", str(metrics["max_consecutive_wins"]))
    if "max_consecutive_losses" in metrics:
        table.add_row("Max Consecutive Losses", str(metrics["max_consecutive_losses"]))

    console.print(table)

    # Display trades table only if --detail flag is set
    if show_detail and trades:
        display_trades_table(trades, title="Backtest Trades")
    elif not show_detail:
        console.print(f"[dim]Total trades: {metrics.get('total_trades', 0)}[/dim]")
    console.print()


def display_trades_table(trades: list, title: str = "Trades"):
    """Display trades in a formatted table.

    Args:
        trades: List of trade dictionaries
        title: Table title
    """
    if not trades:
        return

    table = Table(
        title=f"[bold cyan]{title} ({len(trades)})[/bold cyan]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold yellow",
        padding=(0, 1),
    )

    # Add columns
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Entry Time", style="cyan", width=16)
    table.add_column("Exit Time", style="cyan", width=16)
    table.add_column("Entry", style="white", width=10, justify="right")
    table.add_column("Exit", style="white", width=10, justify="right")
    table.add_column("Qty", style="dim", width=8, justify="right")
    table.add_column("P&L", style="white", width=12, justify="right")
    table.add_column("Return %", style="white", width=10, justify="right")
    table.add_column("Reason", style="dim", width=12)
    table.add_column("MAE", style="dim", width=8, justify="right")
    table.add_column("MFE", style="dim", width=8, justify="right")

    # Add trade rows
    for idx, trade in enumerate(trades, 1):
        # Parse timestamps
        entry_time = trade.get("entry_time", "")
        exit_time = trade.get("exit_time", "")

        # Format timestamps (remove timezone for display)
        try:
            if entry_time:
                dt = datetime.fromisoformat(entry_time.replace("Z", "+00:00"))
                entry_time = dt.strftime("%Y-%m-%d %H:%M")
            if exit_time:
                dt = datetime.fromisoformat(exit_time.replace("Z", "+00:00"))
                exit_time = dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            pass

        entry_price = trade.get("entry_price", 0)
        exit_price = trade.get("exit_price", 0)
        quantity = trade.get("quantity", 0)
        pnl = trade.get("pnl", 0)
        return_pct = trade.get("return_pct", 0)
        exit_reason = trade.get("exit_reason", "")
        mae = trade.get("mae", 0)
        mfe = trade.get("mfe", 0)

        # Color code P&L
        pnl_color = "green" if pnl >= 0 else "red"
        return_color = "green" if return_pct >= 0 else "red"

        # Format values
        entry_str = f"{entry_price:.2f}" if entry_price else "-"
        exit_str = f"{exit_price:.2f}" if exit_price else "-"
        qty_str = f"{quantity:.2f}" if quantity else "-"
        pnl_str = f"[{pnl_color}]{pnl:,.2f}[/{pnl_color}]"
        return_str = f"[{return_color}]{return_pct:.2f}%[/{return_color}]"
        mae_str = f"{mae:.2f}" if mae else "-"
        mfe_str = f"{mfe:.2f}" if mfe else "-"

        table.add_row(
            str(idx),
            entry_time or "-",
            exit_time or "-",
            entry_str,
            exit_str,
            qty_str,
            pnl_str,
            return_str,
            exit_reason or "-",
            mae_str,
            mfe_str,
        )

    console.print()
    console.print(table)
    console.print()


def display_walkforward_results(walkforward: Dict[str, Any], show_detail: bool = False):
    """Display walkforward results.

    Args:
        walkforward: Walkforward results dict
        show_detail: If True, show detailed trade-by-trade breakdown
    """
    metrics = walkforward.get("combined_metrics", {})
    num_windows = walkforward.get("num_windows", 0)
    trades = walkforward.get("trades", [])

    table = Table(
        title="[bold cyan]Walk-Forward Analysis[/bold cyan]",
        box=box.ROUNDED,
        show_header=False,
        padding=(0, 2),
    )
    table.add_column("Metric", style="bold yellow", width=25)
    table.add_column("Value", style="white")

    if num_windows > 0:
        table.add_row("Windows", str(num_windows))

    # Combined metrics (same structure as backtest)
    if "total_trades" in metrics:
        table.add_row("Total Trades", str(metrics["total_trades"]))
    if "win_rate" in metrics:
        table.add_row("Win Rate", f"{metrics['win_rate']:.1%}")
    if "total_pnl" in metrics:
        pnl = metrics["total_pnl"]
        color = "green" if pnl >= 0 else "red"
        table.add_row("Total P&L", f"[{color}]{pnl:,.2f}[/{color}]")
    if "sharpe_ratio" in metrics:
        table.add_row("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
    if "max_drawdown" in metrics:
        table.add_row("Max Drawdown", f"{metrics['max_drawdown']:.1%}")

    console.print(table)

    # Display trades table only if --detail flag is set
    if show_detail and trades:
        display_trades_table(trades, title="Walk-Forward Trades")
    elif not show_detail and trades:
        console.print(f"[dim]Total trades: {metrics.get('total_trades', len(trades))}[/dim]")
    console.print()


def display_montecarlo_results(montecarlo: Dict[str, Any]):
    """Display Monte Carlo results.

    Args:
        montecarlo: Monte Carlo results dict
    """
    table = Table(
        title="[bold cyan]Monte Carlo Simulation[/bold cyan]",
        box=box.ROUNDED,
        show_header=False,
        padding=(0, 2),
    )
    table.add_column("Metric", style="bold yellow", width=25)
    table.add_column("Value", style="white")

    if "num_simulations" in montecarlo:
        table.add_row("Simulations", str(montecarlo["num_simulations"]))
    if "pnl_mean" in montecarlo:
        pnl_mean = montecarlo["pnl_mean"]
        color = "green" if pnl_mean >= 0 else "red"
        table.add_row("Mean P&L", f"[{color}]{pnl_mean:,.2f}[/{color}]")
    if "pnl_std" in montecarlo:
        table.add_row("Std Dev P&L", f"{montecarlo['pnl_std']:,.2f}")
    if "sharpe_mean" in montecarlo:
        table.add_row("Mean Sharpe", f"{montecarlo['sharpe_mean']:.2f}")

    console.print(table)
    console.print()


def display_stress_results(stress: Dict[str, Any], show_detail: bool = False):
    """Display stress test results.

    Args:
        stress: Stress test results dict
        show_detail: If True, show detailed trade-by-trade breakdown
    """
    metrics = stress.get("baseline_metrics", {})
    num_scenarios = stress.get("num_scenarios", 0)
    trades = stress.get("trades", [])

    table = Table(
        title="[bold cyan]Stress Test[/bold cyan]",
        box=box.ROUNDED,
        show_header=False,
        padding=(0, 2),
    )
    table.add_column("Metric", style="bold yellow", width=25)
    table.add_column("Value", style="white")

    if num_scenarios > 0:
        table.add_row("Scenarios", str(num_scenarios))

    # Baseline metrics (same structure as backtest)
    if "total_trades" in metrics:
        table.add_row("Total Trades", str(metrics["total_trades"]))
    if "win_rate" in metrics:
        table.add_row("Win Rate", f"{metrics['win_rate']:.1%}")
    if "total_pnl" in metrics:
        pnl = metrics["total_pnl"]
        color = "green" if pnl >= 0 else "red"
        table.add_row("Total P&L", f"[{color}]{pnl:,.2f}[/{color}]")
    if "sharpe_ratio" in metrics:
        table.add_row("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
    if "max_drawdown" in metrics:
        table.add_row("Max Drawdown", f"{metrics['max_drawdown']:.1%}")

    console.print(table)

    # Display trades table only if --detail flag is set
    if show_detail and trades:
        display_trades_table(trades, title="Stress Test Trades")
    elif not show_detail and trades:
        console.print(f"[dim]Total trades: {metrics.get('total_trades', len(trades))}[/dim]")
    console.print()
