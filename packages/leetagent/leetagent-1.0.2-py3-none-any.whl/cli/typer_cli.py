"""
Typer-based CLI for LeetAgentAuto
Modern command-line interface with rich terminal output
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from modules.auth import LeetCodeAuth
from core.logger import logger
from config import settings

app = typer.Typer(
    name="leetagentauto",
    help="🚀 LeetAgentAuto - AI-powered LeetCode automation tool",
    add_completion=False
)

console = Console()


@app.command("login")
def login_command():
    """
    🔐 Login to LeetCode and save cookies
    
    Opens Chrome browser, waits for manual login, captures cookies,
    and saves them securely for future use.
    """
    from cli.main_cli import login_command as login_func
    login_func()


@app.command("logout")
def logout_command():
    """
    🚪 Logout from LeetCode (delete saved cookies)
    
    Removes locally saved cookies to log out of the session.
    """
    auth = LeetCodeAuth()
    
    console.clear()
    
    # Header
    header = Panel(
        "[bold red]🚪 Logout[/bold red]",
        border_style="red",
        padding=(1, 2)
    )
    console.print(header)
    console.print()
    
    if not auth.cookies_exist():
        console.print("[yellow]⚠️  You're not logged in.[/yellow]")
        console.print("[dim]No cookies found to delete.[/dim]")
        return
    
    # Confirm logout
    if not typer.confirm("Are you sure you want to logout?", default=False):
        console.print("\n[cyan]✓ Logout cancelled.[/cyan]")
        return
    
    # Delete cookies
    try:
        cookie_path = auth.get_cookie_path()
        cookie_path.unlink()
        
        success_panel = Panel(
            "[green]✅ Successfully logged out![/green]\n\n"
            "[dim]All cookies have been deleted.[/dim]",
            title="Success",
            border_style="green",
            padding=(1, 2)
        )
        console.print(success_panel)
        logger.info("User logged out - cookies deleted")
        
    except Exception as e:
        console.print(f"[red]❌ Error during logout: {str(e)}[/red]")
        logger.error(f"Logout error: {e}")


@app.command("session-status")
def session_status_command():
    """
    🔍 Check if your session is valid
    
    Verifies if saved cookies exist and are properly formatted.
    """
    auth = LeetCodeAuth()
    
    console.clear()
    
    # Header
    header = Panel(
        "[bold cyan]🔍 Session Status[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(header)
    console.print()
    
    # Check if cookies exist
    if not auth.cookies_exist():
        panel = Panel(
            "[red]❌ Not logged in[/red]\n\n"
            "[yellow]No saved cookies found.[/yellow]\n\n"
            "[dim]Run 'leetagentauto login' to get started.[/dim]",
            title="Status",
            border_style="red",
            padding=(1, 2)
        )
        console.print(panel)
        return
    
    # Load and validate cookies
    cookies = auth.load_cookies()
    
    if not cookies:
        panel = Panel(
            "[red]❌ Invalid session[/red]\n\n"
            "[yellow]Cookies file is corrupted or empty.[/yellow]\n\n"
            "[dim]Run 'leetagentauto login' to re-authenticate.[/dim]",
            title="Status",
            border_style="red",
            padding=(1, 2)
        )
        console.print(panel)
        return
    
    # Check for required cookies
    has_session = any(
        cookie.get('name') == 'LEETCODE_SESSION' and 
        cookie.get('value') and 
        len(cookie.get('value', '')) > 10
        for cookie in cookies
    )
    
    if has_session:
        cookie_path = auth.get_cookie_path()
        
        # Create status table
        table = Table(show_header=False, box=box.ROUNDED)
        table.add_row("[cyan]Status[/cyan]", "[green]✓ Logged in[/green]")
        table.add_row("[cyan]Cookie file[/cyan]", str(cookie_path))
        table.add_row("[cyan]Cookies count[/cyan]", str(len(cookies)))
        
        panel = Panel(
            table,
            title="[green]Session Valid[/green]",
            border_style="green",
            padding=(1, 2)
        )
        console.print(panel)
        
        console.print("\n[dim]💡 Tip: Session expires after some time. Re-login if automation fails.[/dim]")
    else:
        panel = Panel(
            "[red]❌ Invalid session[/red]\n\n"
            "[yellow]Missing LEETCODE_SESSION cookie.[/yellow]\n\n"
            "[dim]Run 'leetagentauto login' to re-authenticate.[/dim]",
            title="Status",
            border_style="red",
            padding=(1, 2)
        )
        console.print(panel)


@app.command("auto")
def auto_command():
    """
    🚀 Auto mode - Solve today's daily challenge
    
    Automatically fetches today's LeetCode daily challenge,
    generates solution with AI, and submits it.
    """
    from main import main_auto
    
    console.print("\n[bold cyan]🚀 Starting Auto Mode...[/bold cyan]\n")
    exit_code = main_auto()
    raise typer.Exit(code=exit_code)


@app.command("interactive")
def interactive_command():
    """
    🎮 Interactive menu mode
    
    Opens an interactive menu with multiple options:
    - Login/Logout
    - Solve problems
    - Test components
    - View configuration
    """
    from main import main_interactive
    
    main_interactive()


@app.command("direct")
def direct_command(
    url: str = typer.Argument(..., help="LeetCode problem URL"),
    language: str = typer.Option("C#", "--lang", "-l", help="Programming language (C#/Python/Java/JavaScript)")
):
    """
    🎯 Solve a specific problem directly
    
    Provide a LeetCode problem URL and optional language to solve it immediately.
    
    Example:
        leetagentauto direct https://leetcode.com/problems/two-sum/ --lang Python
    """
    from main import main_direct
    
    console.print(f"\n[bold cyan]🎯 Solving problem: {url}[/bold cyan]")
    console.print(f"[dim]Language: {language}[/dim]\n")
    
    exit_code = main_direct(url, language)
    raise typer.Exit(code=exit_code)


@app.command("version")
def version_command():
    """
    📦 Show version information
    """
    from config import settings
    
    console.clear()
    
    panel = Panel(
        f"[bold cyan]{settings.PROJECT_NAME}[/bold cyan]\n\n"
        f"[yellow]Version:[/yellow] {settings.VERSION}\n"
        f"[yellow]Author:[/yellow] {settings.AUTHOR}\n\n"
        f"[dim]AI-powered LeetCode automation tool[/dim]",
        title="About",
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(panel)


def main():
    """Main entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()
