"""Strategy analysis command."""

import json
import sys
import hashlib
import time
from pathlib import Path
from typing import Optional

import click
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich import box
from rich.panel import Panel

from edgelab.api.client import EdgeLabClient
from edgelab.api.exceptions import EdgeLabAPIError, UnauthorizedError, NetworkError
from edgelab.config import get_settings
from edgelab.utils import console, print_success, print_error, print_warning, print_info


def cmd_analyze(
    strategy_file: str,
    symbols: str,
    start_date: str,
    end_date: str,
    ml: bool,
    resolution: str,
    asset_type: str,
):
    """Analyze trading strategy on EdgeLab Cloud.

    Args:
        strategy_file: Path to strategy Python file
        symbols: Comma-separated list of symbols (e.g., "SPY,TSLA")
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        ml: Enable ML optimization
        resolution: Bar resolution (1m, 5m, 15m, 1h, 1d)
        asset_type: Asset type (equity, crypto, forex)
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

    console.print()
    console.print("[bold cyan]📊 EdgeLab Strategy Analysis[/bold cyan]")
    console.print()

    # Read strategy file
    strategy_path = Path(strategy_file)
    if not strategy_path.exists():
        print_error(f"Strategy file not found: {strategy_file}")
        console.print()
        sys.exit(1)

    try:
        strategy_code = strategy_path.read_text()
    except Exception as e:
        print_error(f"Failed to read strategy file: {e}")
        console.print()
        sys.exit(1)

    # Extract required indicators from strategy code
    try:
        from edgelab.utils.indicator_extractor import extract_indicators_from_code
        
        required_indicators = extract_indicators_from_code(strategy_code)
        required_indicators_dict = required_indicators if required_indicators else None
    except Exception as e:
        console.print(f"[yellow]⚠️  Warning: Failed to extract indicators: {e}[/yellow]")
        console.print("[dim]Continuing without indicator extraction...[/dim]")
        required_indicators_dict = None

    # Calculate hash
    code_hash = hashlib.sha256(strategy_code.encode()).hexdigest()

    # Extract strategy name and version (simple parsing)
    strategy_name = strategy_path.stem  # Use filename as default
    strategy_version = "v1"  # Default version

    # Parse symbols
    symbol_list = [s.strip().upper() for s in symbols.split(",")]

    # Display analysis details
    info_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    info_table.add_column("Key", style="bold yellow", width=18)
    info_table.add_column("Value", style="white")

    info_table.add_row("Strategy", strategy_path.name)
    info_table.add_row("Name", strategy_name)
    info_table.add_row("Version", strategy_version)
    info_table.add_row("Code Hash", code_hash[:16] + "...")
    info_table.add_row("", "")
    info_table.add_row("Symbols", ", ".join(symbol_list))
    info_table.add_row("Date Range", f"{start_date} to {end_date}")
    info_table.add_row("Resolution", resolution)
    info_table.add_row("Asset Type", asset_type)
    info_table.add_row("ML Enabled", "Yes" if ml else "No")

    console.print(info_table)
    console.print()

    # Submit to API
    console.print("[dim]Submitting to EdgeLab Cloud...[/dim]")

    try:
        client = EdgeLabClient()
        
        # Build request payload
        payload = {
            "strategy_code": strategy_code,
            "strategy_name": strategy_name,
            "strategy_version": strategy_version,
            "code_hash": code_hash,
            "symbols": symbol_list,
            "start_date": start_date,
            "end_date": end_date,
            "asset_type": asset_type,
            "resolution": resolution,
            "ml_enabled": ml,
        }
        
        # Add required_indicators if extracted
        if required_indicators_dict:
            payload["required_indicators"] = required_indicators_dict
        
        response = client.post(
            "/api/v1/edgelab/analysis",
            data=payload,
            authenticated=True,
        )

        # API wraps response in "data" field
        data = response.get("data", response)
        workflow_id = data["workflow_id"]
        status = data["status"]

        console.print()
        print_success("Analysis job submitted!")
        print_info(f"Workflow ID: {workflow_id}")
        print_info(f"Status: {status}")
        console.print()

        # Poll for results
        console.print("[bold yellow]Running analysis on EdgeLab Cloud...[/bold yellow]")
        console.print("[dim]This may take 2-5 minutes depending on data size and ML settings[/dim]")
        console.print()

        poll_workflow(client, workflow_id)

    except UnauthorizedError:
        console.print()
        print_error("Authentication failed")
        console.print()
        console.print("[dim]Your session may have expired. Please login again:[/dim]")
        console.print("  [cyan]edgelab auth login[/cyan]")
        console.print()
        sys.exit(1)

    except NetworkError as e:
        console.print()
        print_error(f"Network error: {e}")
        console.print()
        sys.exit(1)

    except EdgeLabAPIError as e:
        console.print()
        print_error(f"API error: {e}")
        console.print()
        sys.exit(1)


def poll_workflow(client: EdgeLabClient, workflow_id: str):
    """Poll workflow status and display progress.

    Args:
        client: HTTP client
        workflow_id: Workflow ID to poll
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Processing...", total=100)

        while True:
            try:
                response = client.get(
                    f"/api/v1/edgelab/workflows/{workflow_id}",
                    authenticated=True,
                )

                # API wraps response in "data" field
                workflow = response.get("data", response)
                status = workflow["status"]
                current_progress = workflow.get("progress", 0)

                # Update progress bar
                progress.update(task, completed=current_progress)

                if status == "completed":
                    progress.update(task, completed=100)
                    console.print()
                    print_success("Analysis completed!")
                    console.print()

                    # Display results
                    display_results(workflow)
                    break

                elif status == "failed":
                    console.print()
                    print_error("Analysis failed")
                    error_msg = workflow.get("error", "Unknown error")
                    console.print(f"[red]{error_msg}[/red]")
                    console.print()
                    sys.exit(1)

                # Continue polling
                time.sleep(2)

            except KeyboardInterrupt:
                console.print()
                print_warning("Interrupted by user")
                console.print()
                console.print("[dim]Analysis is still running on the server.[/dim]")
                console.print(
                    f"[dim]Check status with:[/dim] [cyan]edgelab results show {workflow_id}[/cyan]"
                )
                console.print()
                sys.exit(0)

            except Exception as e:
                console.print()
                print_error(f"Failed to poll status: {e}")
                console.print()
                sys.exit(1)


def display_results(workflow_data: dict):
    """Display analysis results in rich format.

    Args:
        workflow_data: Workflow data from API
    """
    metadata = workflow_data.get("metadata", {})

    if not metadata:
        print_warning("No results data available")
        return

    # Display backtest results
    if "backtest" in metadata:
        backtest = metadata["backtest"]

        table = Table(
            title="[bold cyan]BACKTEST RESULTS[/bold cyan]",
            box=box.ROUNDED,
            show_header=False,
        )
        table.add_column("Metric", style="bold yellow", width=25)
        table.add_column("Value", style="white")

        table.add_row("Total Trades", str(backtest.get("total_trades", 0)))
        table.add_row("Win Rate", f"{backtest.get('win_rate', 0):.1%}")
        table.add_row("Total P&L", f"${backtest.get('total_pnl', 0):,.2f}")
        table.add_row("Sharpe Ratio", f"{backtest.get('sharpe_ratio', 0):.2f}")
        table.add_row("Max Drawdown", f"{backtest.get('max_drawdown', 0):.1%}")

        console.print(table)
        console.print()

    # Show workflow ID for detailed results
    console.print("[bold yellow]📋 View detailed results:[/bold yellow]")
    console.print(f"  [cyan]edgelab results show {workflow_data['workflow_id']}[/cyan]")
    console.print()
