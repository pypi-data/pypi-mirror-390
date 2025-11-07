"""Workspace initialization command."""

import sys
import shutil
from pathlib import Path

from edgelab.utils import console, print_success, print_error, print_info


def cmd_init(folder: str):
    """Initialize EdgeLab workspace with example strategies.

    Args:
        folder: Workspace folder name
    """
    console.print()
    console.print(f"[bold cyan]Creating EdgeLab Workspace:[/bold cyan] {folder}")
    console.print()

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

        # Copy example strategies
        import edgelab.examples
        examples_dir = Path(edgelab.examples.__file__).parent

        example_files = [
            "simple_rsi.py",
            "ema_crossover.py",
        ]

        console.print("[bold yellow]📝 Creating example strategies:[/bold yellow]")
        for filename in example_files:
            src = examples_dir / filename
            dst = workspace_path / "strategies" / filename

            if src.exists():
                shutil.copy(src, dst)
                print_success(f"  strategies/{filename}")
            else:
                print_error(f"  Example not found: {filename}")

        console.print()

        # Create README
        readme_content = """# EdgeLab Workspace

This workspace contains your trading strategies and analysis results.

## Folder Structure

- `strategies/` - Your trading strategy files
- `results/` - Analysis results (future feature)

## Example Strategies

### simple_rsi.py
Mean reversion strategy using RSI indicator.
- Buy when RSI < 30 (oversold)
- Sell when RSI > 70 (overbought)

### ema_crossover.py
Trend following strategy using EMA crossovers.
- Buy on golden cross (fast EMA crosses above slow EMA)
- Sell on death cross (fast EMA crosses below slow EMA)

## Running Analysis

```bash
# Analyze strategy on single symbol
edgelab analyze strategies/simple_rsi.py SPY 2023-01-01 2023-12-31

# Analyze on multiple symbols
edgelab analyze strategies/simple_rsi.py SPY,TSLA,NVDA 2023-01-01 2023-12-31

# With ML optimization
edgelab analyze --ml strategies/simple_rsi.py SPY,QQQ 2023-01-01 2023-12-31
```

## Next Steps

1. Review example strategies
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
        console.print(f"  2. Review example strategies:")
        console.print(f"     [cyan]cat strategies/simple_rsi.py[/cyan]")
        console.print()
        console.print(f"  3. Run your first analysis:")
        console.print(f"     [cyan]edgelab analyze strategies/simple_rsi.py SPY 2023-01-01 2023-12-31[/cyan]")
        console.print()

    except Exception as e:
        console.print()
        print_error(f"Failed to create workspace: {e}")
        console.print()
        sys.exit(1)
