"""Workspace initialization command."""

import sys
from pathlib import Path

from edgelab.api.client import EdgeLabClient
from edgelab.api.exceptions import EdgeLabAPIError
from edgelab.config import get_settings
from edgelab.utils import console, print_success, print_error, print_info


def cmd_init(folder: str):
    """Initialize EdgeLab workspace with system templates from marketplace.

    Args:
        folder: Workspace folder name
    """
    console.print()
    console.print(f"[bold cyan]Creating EdgeLab Workspace:[/bold cyan] {folder}")
    console.print()

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

    workspace_path = Path(folder).resolve()

    # Check if folder already exists
    if workspace_path.exists():
        print_error(f"Folder already exists: {workspace_path}")
        console.print()
        console.print("[dim]Choose a different name or remove the existing folder.[/dim]")
        console.print()
        sys.exit(1)

    try:
        # Create workspace structure
        workspace_path.mkdir(parents=True)
        (workspace_path / "strategies").mkdir()
        (workspace_path / "results").mkdir()

        print_success(f"Created workspace: {workspace_path}")
        console.print()

        # Fetch system templates from API
        client = EdgeLabClient()

        console.print("[bold yellow]📥 Fetching system templates from marketplace...[/bold yellow]")
        console.print()

        # Fetch public strategies, prefer system strategies
        try:
            # Try to get system strategies first (filter by author_type='system' via tags or just get all public)
            response = client.get(
                "/api/v1/edgelab/marketplace/strategies",
                authenticated=True,
                params={"limit": 50, "sort": "recent"},
            )
            strategies = response.get("data", [])

            # Filter for system strategies (author_type='system')
            system_strategies = [s for s in strategies if s.get("author_type") == "system"]

            # If we have system strategies, use them; otherwise use any public strategies
            selected_strategies = system_strategies[:2] if len(system_strategies) >= 2 else strategies[:2]

            if len(selected_strategies) < 2:
                print_error("Not enough public strategies available. Need at least 2 system templates.")
                console.print()
                sys.exit(1)

            # Select 2 strategies with diverse tags if possible
            if len(selected_strategies) > 2:
                # Try to get one mean-reversion and one trend-following
                mean_reversion = None
                trend_following = None
                for s in selected_strategies:
                    tags = s.get("tags", [])
                    if not mean_reversion and "mean-reversion" in tags:
                        mean_reversion = s
                    if not trend_following and "trend-following" in tags:
                        trend_following = s

                if mean_reversion and trend_following:
                    selected_strategies = [mean_reversion, trend_following]
                else:
                    selected_strategies = selected_strategies[:2]

            # Download strategy code
            strategy_files = []
            for strategy in selected_strategies:
                strategy_id = strategy.get("id")
                strategy_name = strategy.get("name", "strategy")
                strategy_description = strategy.get("description", "")

                try:
                    code = client.get_strategy_code(strategy_id)
                    if not code:
                        print_error(f"  Failed to fetch code for {strategy_name}")
                        continue

                    # Save to workspace
                    filename = f"{strategy_name}.py"
                    filepath = workspace_path / "strategies" / filename
                    filepath.write_text(code)

                    strategy_files.append({
                        "filename": filename,
                        "name": strategy_name,
                        "description": strategy_description,
                    })
                    print_success(f"  strategies/{filename}")
                except EdgeLabAPIError as e:
                    print_error(f"  Failed to fetch {strategy_name}: {e}")
                    continue

            if not strategy_files:
                print_error("Failed to download any strategy templates.")
                console.print()
                sys.exit(1)

            console.print()

            # Create README
            strategy_list = "\n".join(
                [
                    f"### {s['filename']}\n{s['description']}" for s in strategy_files
                ]
            )

            readme_content = f"""# EdgeLab Workspace

This workspace contains your trading strategies and analysis results.

## Folder Structure

- `strategies/` - Your trading strategy files
- `results/` - Analysis results (future feature)

## System Templates

{strategy_list}

## Running Analysis

```bash
# Analyze strategy on single symbol
edgelab analyze strategies/{strategy_files[0]['filename']} SPY 2023-01-01 2023-12-31

# Analyze on multiple symbols
edgelab analyze strategies/{strategy_files[0]['filename']} SPY,TSLA,NVDA 2023-01-01 2023-12-31

# With ML optimization
edgelab analyze --ml strategies/{strategy_files[0]['filename']} SPY,QQQ 2023-01-01 2023-12-31
```

## Next Steps

1. Review system templates
2. Modify parameters or create your own strategy
3. Run analysis with `edgelab analyze`
4. View results with `edgelab results list`

## Documentation

- Full docs: https://docs.edgelab.com
- API reference: https://docs.edgelab.com/api
- Strategy examples: https://docs.edgelab.com/strategies
"""

            readme_path = workspace_path / "README.md"
            readme_path.write_text(readme_content)
            print_success("  README.md")

            console.print()
            console.print("[bold green]✨ Workspace ready![/bold green]")
            console.print()

            # Show next steps
            console.print("[bold yellow]Next steps:[/bold yellow]")
            console.print(f"  1. Navigate to workspace:")
            console.print(f"     [cyan]cd {folder}[/cyan]")
            console.print()
            console.print(f"  2. Review system templates:")
            console.print(f"     [cyan]cat strategies/{strategy_files[0]['filename']}[/cyan]")
            console.print()
            console.print(f"  3. Run your first analysis:")
            console.print(f"     [cyan]edgelab analyze strategies/{strategy_files[0]['filename']} SPY 2023-01-01 2023-12-31[/cyan]")
            console.print()

        except EdgeLabAPIError as e:
            print_error(f"API error: {e}")
            console.print()
            sys.exit(1)

    except Exception as e:
        console.print()
        print_error(f"Failed to create workspace: {e}")
        console.print()
        sys.exit(1)
