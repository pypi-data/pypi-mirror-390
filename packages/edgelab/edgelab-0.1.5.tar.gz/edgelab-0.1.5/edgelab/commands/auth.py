"""Authentication commands implementation."""

import sys
import click
from rich.table import Table
from rich import box

from edgelab.api.client import EdgeLabClient
from edgelab.api.auth import AuthAPI
from edgelab.api.exceptions import (
    ValidationError,
    AuthenticationError,
    NetworkError,
    EdgeLabAPIError,
)
from edgelab.config import get_settings
from edgelab.utils import console, print_success, print_error, print_warning, print_info


def cmd_signup():
    """Sign up for new EdgeLab account."""
    console.print()
    console.print("[bold cyan]EdgeLab Sign Up[/bold cyan]")
    console.print()

    # Get email
    email = click.prompt("Email", type=str)

    # Get password (with confirmation)
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)

    console.print()
    console.print("Creating account...", style="dim")

    try:
        # Call API
        client = EdgeLabClient()
        auth_api = AuthAPI(client)
        result = auth_api.signup(email, password)

        # Save tokens
        settings = get_settings()
        settings.save_auth(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            expires_at=result["expires_at"],
            user={
                "id": result.get("user_id", "unknown"),
                "email": email,
                "role": "free",
            },
        )

        console.print()
        print_success("Account created successfully!")
        print_success(f"Logged in as: {email}")
        print_success(f"Tokens saved to: {settings.auth_file}")
        console.print()

        # Show next steps
        console.print("[bold yellow]Next steps:[/bold yellow]")
        console.print("  1. Initialize workspace:  [cyan]edgelab init my-strategies[/cyan]")
        console.print("  2. Analyze a strategy:    [cyan]edgelab analyze --help[/cyan]")
        console.print()

    except ValidationError as e:
        console.print()
        print_error(f"Signup failed: {e}")
        console.print()
        console.print("[dim]Common issues:[/dim]")
        console.print("  • Email already registered")
        console.print("  • Password too weak (min 8 characters)")
        console.print("  • Invalid email format")
        console.print()
        sys.exit(1)

    except NetworkError as e:
        console.print()
        print_error(f"Network error: {e}")
        console.print()
        console.print("[dim]Please check:[/dim]")
        console.print("  • Internet connection")
        console.print("  • EdgeLab server status")
        console.print()
        sys.exit(1)

    except EdgeLabAPIError as e:
        console.print()
        print_error(f"Signup failed: {e}")
        console.print()
        sys.exit(1)


def cmd_login():
    """Login to EdgeLab."""
    console.print()
    console.print("[bold cyan]EdgeLab Login[/bold cyan]")
    console.print()

    # Get credentials
    email = click.prompt("Email", type=str)
    password = click.prompt("Password", hide_input=True)

    console.print()
    console.print("Authenticating...", style="dim")

    try:
        # Call API
        client = EdgeLabClient()
        auth_api = AuthAPI(client)
        result = auth_api.login(email, password)

        # Save tokens
        settings = get_settings()
        settings.save_auth(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            expires_at=result["expires_at"],
            user={
                "id": result.get("user_id", "unknown"),
                "email": email,
                "role": "free",
            },
        )

        console.print()
        print_success("Login successful!")
        print_success(f"Logged in as: {email}")
        print_success(f"Tokens saved to: {settings.auth_file}")
        console.print()

    except AuthenticationError as e:
        console.print()
        print_error(f"Login failed: Invalid email or password")
        console.print()
        console.print("[dim]Forgot password?[/dim]")
        console.print("  Visit: https://pantry-chef.com/forgot-password")
        console.print()
        sys.exit(1)

    except NetworkError as e:
        console.print()
        print_error(f"Network error: {e}")
        console.print()
        sys.exit(1)

    except EdgeLabAPIError as e:
        console.print()
        print_error(f"Login failed: {e}")
        console.print()
        sys.exit(1)


def cmd_logout():
    """Logout from EdgeLab."""
    settings = get_settings()

    if not settings.is_authenticated():
        console.print()
        print_warning("Not logged in")
        console.print()
        sys.exit(1)

    console.print()
    console.print("Logging out...", style="dim")

    try:
        # Call logout API to invalidate refresh token
        refresh_token = settings.get_refresh_token()
        if refresh_token:
            client = EdgeLabClient()
            auth_api = AuthAPI(client)
            auth_api.logout(refresh_token)

        # Clear local tokens
        settings.clear_auth()

        console.print()
        print_success("Logged out successfully")
        print_info(f"Removed: {settings.auth_file}")
        console.print()

    except Exception as e:
        # Even if API call fails, clear local tokens
        settings.clear_auth()
        console.print()
        print_success("Logged out (local tokens cleared)")
        console.print()


def cmd_whoami():
    """Show current authentication status."""
    settings = get_settings()

    console.print()

    if not settings.is_authenticated():
        print_warning("Not logged in")
        console.print()
        console.print("[dim]To login:[/dim]")
        console.print("  [cyan]edgelab login[/cyan]")
        console.print()
        console.print("[dim]To sign up:[/dim]")
        console.print("  [cyan]edgelab signup[/cyan]")
        console.print()
        sys.exit(1)

    # Get user info
    user = settings.get_user()
    auth = settings.load_auth()

    # Create table
    table = Table(
        title="[bold cyan]EdgeLab Authentication Status[/bold cyan]",
        box=box.ROUNDED,
        show_header=False,
        padding=(0, 1),
    )

    table.add_column("Key", style="bold yellow", width=20)
    table.add_column("Value", style="white")

    table.add_row("Status", "[green]✓ Authenticated[/green]")
    table.add_row("Email", user.get("email", "Unknown"))
    table.add_row("User ID", user.get("id", "Unknown"))
    table.add_row("Plan", user.get("role", "free").capitalize())
    table.add_row("Config", str(settings.auth_file))

    console.print(table)
    console.print()
