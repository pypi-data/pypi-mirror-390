"""EdgeLab CLI - Main entry point with rich-click interface."""

import sys
from typing import Optional

import click
import rich_click as click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from edgelab import __version__

# Configure rich-click for beautiful output
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_ERRORS_SUGGESTION = "yellow italic"
click.rich_click.ERRORS_SUGGESTION = "Try running the '--help' flag for more information."
click.rich_click.ERRORS_EPILOGUE = ""
click.rich_click.MAX_WIDTH = 100
click.rich_click.STYLE_OPTION = "bold cyan"
click.rich_click.STYLE_ARGUMENT = "bold yellow"
click.rich_click.STYLE_COMMAND = "bold green"

# Console instance for rich output
console = Console()


def print_banner():
    """Print EdgeLab banner."""
    banner = """
[bold cyan]╔═══════════════════════════════════════════════════════╗[/bold cyan]
[bold cyan]║[/bold cyan]                  [bold white]EdgeLab CLI[/bold white]                     [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]     [dim]Algorithmic Trading Strategy Analysis[/dim]       [bold cyan]║[/bold cyan]
[bold cyan]╚═══════════════════════════════════════════════════════╝[/bold cyan]
    """
    console.print(banner)


@click.group(
    invoke_without_command=True,
    help="""
    [bold cyan]EdgeLab CLI[/bold cyan] - Algorithmic Trading Strategy Analysis Platform

    Write Python strategies locally, analyze them on EdgeLab Cloud, and view
    results with beautiful formatted output.

    [bold yellow]Quick Start:[/bold yellow]

      $ edgelab signup          # Create account
      $ edgelab login           # Login
      $ edgelab init my-strategies   # Create workspace
      $ edgelab analyze strategies/simple_rsi.py SPY 2023-01-01 2023-12-31

    [bold yellow]Example Commands:[/bold yellow]

      $ edgelab analyze strategies/my_rsi.py SPY,TSLA 2023-01-01 2023-12-31
      $ edgelab analyze --ml strategies/ml_rsi.py SPY 2023-01-01 2023-12-31
      $ edgelab results list
      $ edgelab strategies list
    """,
)
@click.version_option(
    version=__version__,
    prog_name="edgelab",
    message="%(prog)s version %(version)s",
)
@click.pass_context
def main(ctx: click.Context):
    """EdgeLab CLI - Algorithmic Trading Strategy Analysis."""
    # If no command provided, show banner and help
    if ctx.invoked_subcommand is None:
        print_banner()
        console.print()
        click.echo(ctx.get_help())


@main.command(
    help="""
    [bold]Display EdgeLab CLI version and system information.[/bold]

    Shows the current version of EdgeLab CLI installed on your system,
    along with Python version and platform information.
    """
)
def version():
    """Display version information."""
    import platform

    # Create info table
    table = Table(
        title="[bold cyan]EdgeLab CLI Version Info[/bold cyan]",
        box=box.ROUNDED,
        show_header=False,
        padding=(0, 1),
    )

    table.add_column("Key", style="bold yellow", width=20)
    table.add_column("Value", style="white")

    table.add_row("EdgeLab CLI", f"v{__version__}")
    table.add_row("Python", platform.python_version())
    table.add_row("Platform", platform.platform())
    table.add_row("Architecture", platform.machine())

    console.print()
    console.print(table)
    console.print()

    # Print status
    console.print("✨ EdgeLab CLI is installed and ready!", style="bold green")
    console.print()
    console.print("Next steps:", style="bold yellow")
    console.print("  1. Sign up:  [cyan]edgelab signup[/cyan]")
    console.print("  2. Login:    [cyan]edgelab login[/cyan]")
    console.print("  3. Get help: [cyan]edgelab --help[/cyan]")
    console.print()


# Placeholder commands (will implement next)
@main.group(
    help="""
    [bold]Authentication commands.[/bold]

    Manage your EdgeLab account authentication.
    """
)
def auth():
    """Authentication commands."""
    pass


@auth.command()
def signup():
    """Create a new EdgeLab account."""
    from edgelab.commands.auth import cmd_signup

    cmd_signup()


@auth.command()
def login():
    """Login to EdgeLab."""
    from edgelab.commands.auth import cmd_login

    cmd_login()


@auth.command()
def logout():
    """Logout from EdgeLab."""
    from edgelab.commands.auth import cmd_logout

    cmd_logout()


@auth.command()
def whoami():
    """Show current authentication status."""
    from edgelab.commands.auth import cmd_whoami

    cmd_whoami()


@main.command(
    help="""
    [bold]Initialize a new EdgeLab workspace.[/bold]

    Creates a new workspace with system templates from marketplace.
    Requires authentication - please login first with 'edgelab auth login'.
    """
)
@click.argument("folder", type=str)
def init(folder: str):
    """Initialize workspace with system templates from marketplace."""
    from edgelab.commands.workspace import cmd_init

    cmd_init(folder)


@main.command(
    help="""
    [bold]Analyze a trading strategy on EdgeLab Cloud.[/bold]

    Submits your strategy for server-side analysis with 4 engines:
    - Backtest (in-sample)
    - Walk-Forward (out-of-sample validation)
    - Monte Carlo (1000 simulations)
    - Stress Testing (historical crises)
    """
)
@click.argument("strategy-file", type=click.Path(exists=True))
@click.argument("symbols", type=str)
@click.argument("start-date", type=str)
@click.argument("end-date", type=str)
@click.option(
    "--ml",
    is_flag=True,
    help="Enable ML optimization (trains model to find optimal parameters)",
)
@click.option(
    "--resolution",
    type=click.Choice(["1m", "5m", "15m", "1h", "1d"]),
    default="5m",
    help="Bar resolution (default: 5m)",
)
@click.option(
    "--asset-type",
    type=click.Choice(["equity", "crypto", "forex"]),
    default="equity",
    help="Asset type (default: equity)",
)
def analyze(
    strategy_file: str,
    symbols: str,
    start_date: str,
    end_date: str,
    ml: bool,
    resolution: str,
    asset_type: str,
):
    """Analyze trading strategy."""
    from edgelab.commands.analyze import cmd_analyze

    cmd_analyze(strategy_file, symbols, start_date, end_date, ml, resolution, asset_type)


@main.group(
    help="""
    [bold]Manage analysis results.[/bold]

    View and explore your backtesting results.
    """
)
def results():
    """Results management commands."""
    pass


@results.command(name="list")
def results_list():
    """List all analysis runs."""
    console.print("[yellow]⚠️  Coming soon![/yellow] List results.")


@results.command()
@click.argument("workflow-id", type=str)
@click.option(
    "--detail",
    is_flag=True,
    help="Show detailed trade-by-trade breakdown",
)
def show(workflow_id: str, detail: bool):
    """Show detailed results for a workflow."""
    from edgelab.commands.results import cmd_results_show

    cmd_results_show(workflow_id, show_detail=detail)


@main.group(
    help="""
    [bold]Manage trading strategies.[/bold]

    View and manage your strategies stored on EdgeLab Cloud.
    """
)
def strategies():
    """Strategy management commands."""
    pass


@strategies.command(name="list")
def strategies_list():
    """List all your strategies."""
    console.print("[yellow]⚠️  Coming soon![/yellow] List strategies.")


@strategies.command()
@click.argument("name", type=str)
@click.argument("version", type=str)
def show(name: str, version: str):
    """Show strategy details."""
    console.print(f"[yellow]⚠️  Coming soon![/yellow] Show strategy: {name} {version}")


@main.group(
    help="""
    [bold]Browse and manage public strategies marketplace.[/bold]

    Discover, clone, and fork public trading strategies.
    """
)
def marketplace():
    """Marketplace commands."""
    pass


@marketplace.command(name="list")
@click.option(
    "--sort",
    type=click.Choice(["sharpe", "return", "clones", "recent"]),
    default="sharpe",
    help="Sort order (default: sharpe)",
)
@click.option("--tags", type=str, help="Comma-separated tags to filter by")
@click.option("--min-sharpe", type=float, help="Minimum Sharpe ratio filter")
@click.option("--max-drawdown", type=float, help="Maximum drawdown filter")
def marketplace_list(sort: str, tags: str, min_sharpe: float, max_drawdown: float):
    """List public strategies in marketplace."""
    from edgelab.commands.marketplace.list import cmd_marketplace_list

    cmd_marketplace_list(sort=sort, tags=tags, min_sharpe=min_sharpe, max_drawdown=max_drawdown)


@marketplace.command()
@click.argument("strategy-id", type=str)
def show(strategy_id: str):
    """Show detailed strategy information."""
    from edgelab.commands.marketplace.show import cmd_marketplace_show

    cmd_marketplace_show(strategy_id)


@marketplace.command()
@click.argument("strategy-id", type=str)
@click.option("--name", type=str, required=True, help="Name for forked strategy")
@click.option("--description", type=str, help="Description for forked strategy")
def fork(strategy_id: str, name: str, description: str):
    """Fork a public strategy with modifications."""
    from edgelab.commands.marketplace.fork import cmd_marketplace_fork

    cmd_marketplace_fork(strategy_id, name, description)


if __name__ == "__main__":
    main()
