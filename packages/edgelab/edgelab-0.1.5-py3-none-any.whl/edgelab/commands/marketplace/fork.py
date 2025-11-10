"""Marketplace fork command."""

import sys

from edgelab.api.client import EdgeLabClient
from edgelab.api.exceptions import EdgeLabAPIError
from edgelab.config import get_settings
from edgelab.utils import console, print_error, print_success, print_info


def cmd_marketplace_fork(strategy_id: str, name: str, description: str = None):
    """Fork a public strategy with modifications.

    Args:
        strategy_id: Strategy ID to fork
        name: Name for forked strategy
        description: Optional description
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
        payload = {"name": name}
        if description:
            payload["description"] = description

        response = client.post(
            f"/api/v1/edgelab/marketplace/strategies/{strategy_id}/fork",
            data=payload,
            authenticated=True,
        )

        data = response.get("data", {})
        new_id = data.get("id")
        new_name = data.get("name")

        console.print()
        print_success(f"Strategy forked successfully!")
        console.print()
        print_info(f"New strategy ID: {new_id}")
        print_info(f"Name: {new_name}")
        console.print()

    except EdgeLabAPIError as e:
        print_error(f"API error: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to fork strategy: {e}")
        sys.exit(1)

