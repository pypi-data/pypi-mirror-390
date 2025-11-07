"""
LeetAgent - Global Typer-based CLI

Exports a Typer app named `app` so packaging can expose the global command `leetagent`.
Keeps Rich UI helpers and provides command implementations that delegate to modules and main.
"""

import json
import os
import sys
from pathlib import Path
import subprocess
from typing import Dict, Optional, Tuple
import typer

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

from config import settings
from modules.auth import LeetCodeAuth
from core.logger import logger


# Configuration keys
CONFIG_KEYS: Dict[str, str] = {
    "GEMINI_API_KEY": "Gemini API Key",
    "TELEGRAM_TOKEN": "Telegram Bot Token",
    "CHAT_ID": "Telegram Chat ID",
    "PREFERRED_LANGUAGE": "Preferred Coding Language",
}

KEYRING_SERVICE = "leetagent"

# Supported languages
SUPPORTED_LANGUAGES = [
    "Python", "Java", "C++", "C", "C#", "JavaScript", "TypeScript",
    "Go", "Rust", "Swift", "Kotlin", "Ruby", "PHP", "Scala"
]

app = typer.Typer(
    name="leetagent",
    help=(
        "🚀 LeetAgent - AI-powered LeetCode automation tool\n"
        "\n"
        "Quick Start:\n"
        "  1. Run 'leetagent config' to set up your credentials\n"
        "  2. Run 'leetagent login' to authenticate with LeetCode\n"
        "  3. Run 'leetagent auto' to solve today's challenge\n"
        "\n"
        "Use 'leetagent --help' to see all available commands."
    ),
    add_completion=False,
)
console = Console()


def display_welcome():
    """Display welcome banner with ASCII art"""
    
    ascii_art = """


    ██╗     ███████╗███████╗████████╗ █████╗  ██████╗ ███████╗███╗   ██╗████████╗
    ██║     ██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
    ██║     █████╗  █████╗     ██║   ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   
    ██║     ██╔══╝  ██╔══╝     ██║   ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   
    ███████╗███████╗███████╗   ██║   ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   
    ╚══════╝╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   
                                                                             

    """
    
    welcome_text = Text(ascii_art, style="bold cyan")
    
    info_text = Text()
    info_text.append(f"\n{settings.PROJECT_NAME}\n", style="bold yellow")
    info_text.append(f"Version: {settings.VERSION}\n", style="dim")
    info_text.append(f"Author: {settings.AUTHOR}\n", style="dim")
    info_text.append("\nAutomated LeetCode problem solving with AI \n", style="italic")
    
    panel = Panel(
        welcome_text + info_text,
        title="Welcome",
        border_style="bright_blue",
        padding=(1, 2)
    )
    
    console.print(panel)


def display_auto_welcome():
    """Display compact welcome banner for auto mode"""
    
    welcome = Text()
    welcome.append("🤖 ", style="bold cyan")
    welcome.append("LeetCode Agent Automation\n", style="bold yellow")
    welcome.append(f"Starting automatic daily challenge solver...\n", style="dim")
    
    panel = Panel(
        welcome,
        border_style="bright_blue",
        padding=(0, 2)
    )
    
    console.print(panel)


def display_menu():
    """Display main menu options"""
    
    table = Table(title="", show_header=True, header_style="bold magenta")
    table.add_column("Option", style="cyan", width=10)
    table.add_column("Description", style="white")
    
    table.add_row("1", "Solve Today's Challenge")
    table.add_row("2", "Solve by Problem URL")
    table.add_row("3", "Solve by Difficulty")
    table.add_row("4", "Show Streak Stats")
    table.add_row("5", "Exit")
    
    console.print(table)


def prompt_problem_url() -> str:
    """Prompt user for LeetCode problem URL"""
    return Prompt.ask(
        "\n[bold yellow]Enter LeetCode problem URL[/bold yellow]",
        default="https://leetcode.com/problems/two-sum/"
    )


def prompt_language() -> str:
    """Prompt user for programming language"""
    # Use configured preferred language as default
    default_lang = settings.PREFERRED_LANGUAGE if settings.PREFERRED_LANGUAGE else "Python"
    
    return Prompt.ask(
        "[bold yellow]Select language[/bold yellow]",
        choices=["C#", "Python", "Java", "JavaScript", "C++", "TypeScript", "Go"],
        default=default_lang
    )


def confirm_action(message: str) -> bool:
    """Ask for user confirmation"""
    return Confirm.ask(f"[bold yellow]{message}[/bold yellow]")


def display_config():
    """Display current configuration"""
    
    config_table = Table(title="Configuration", show_header=True)
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    
    # Mask sensitive data
    api_key_masked = settings.GEMINI_API_KEY[:10] + "..." if settings.GEMINI_API_KEY else "Not set"
    bot_token_masked = settings.TELEGRAM_BOT_TOKEN[:10] + "..." if settings.TELEGRAM_BOT_TOKEN else "Not set"
    
    config_table.add_row("Project Name", settings.PROJECT_NAME)
    config_table.add_row("Version", settings.VERSION)
    config_table.add_row("Gemini API Key", api_key_masked)
    config_table.add_row("Gemini Model", settings.GEMINI_MODEL_NAME)
    config_table.add_row("Telegram Bot Token", bot_token_masked)
    config_table.add_row("Chat IDs", ", ".join(settings.get_chat_ids()))
    config_table.add_row("Max AI Attempts", str(settings.MAX_AI_ATTEMPTS))
    config_table.add_row("Cookies Path", str(settings.COOKIES_PATH))
    config_table.add_row("Log Level", settings.LOG_LEVEL)
    
    console.print(config_table)


def display_problem_info(problem: dict):
    """Display problem information in formatted table"""
    from rich.text import Text
    
    info_table = Table(title="Problem Information", show_header=False, box=box.ROUNDED)
    info_table.add_column("Field", style="cyan bold", width=20)
    info_table.add_column("Value", style="white", overflow="fold")
    
    info_table.add_row("Title", problem.get('title', 'Unknown'))
    info_table.add_row("ID", f"#{problem.get('questionFrontendId', 'Unknown')}")
    
    # Color-code difficulty
    difficulty = problem.get('difficulty', 'Unknown')
    if difficulty == 'Easy':
        diff_text = Text(difficulty, style="green bold")
    elif difficulty == 'Medium':
        diff_text = Text(difficulty, style="yellow bold")
    elif difficulty == 'Hard':
        diff_text = Text(difficulty, style="red bold")
    else:
        diff_text = Text(difficulty, style="white")
    info_table.add_row("Difficulty", diff_text)
    
    # Handle both topicTags (list of dicts) and topics (list of strings)
    if 'topics' in problem:
        topics = ", ".join(problem.get('topics', [])[:5])
    else:
        topics = ", ".join([tag['name'] for tag in problem.get('topicTags', [])[:5]])
    info_table.add_row("Topics", topics or "None")
    
    # Add link if available
    if 'link' in problem:
        info_table.add_row("Link", problem.get('link', ''))
    
    # Add likes/dislikes if available
    if 'likes' in problem:
        stats = f"👍 {problem.get('likes', 0)} | 👎 {problem.get('dislikes', 0)}"
        info_table.add_row("Stats", stats)
    
    console.print(info_table)
    
    # Show full description in a separate panel with better formatting
    content = problem.get('content', '')
    if content:
        console.print("\n[bold cyan]Description:[/bold cyan]")
        # Limit to first 500 chars for readability
        desc_text = content[:500] + "..." if len(content) > 500 else content
        desc_panel = Panel(
            desc_text,
            border_style="blue",
            padding=(1, 2)
        )
        console.print(desc_panel)


def display_progress(message: str):
    """Display progress message"""
    console.print(f"\n[bold blue]→[/bold blue] {message}")


def display_success(message: str):
    """Display success message"""
    console.print(f"\n[bold green]✓[/bold green] {message}")


def display_error(message: str):
    """Display error message"""
    console.print(f"\n[bold red]✗[/bold red] {message}")


def display_warning(message: str):
    """Display warning message"""
    console.print(f"\n[bold yellow]⚠[/bold yellow] {message}")


def create_spinner_context(description: str):
    """Create a progress spinner context manager"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        console=console
    )


def display_code_preview(code: str, language: str = "csharp"):
    """Display code in a syntax-highlighted panel"""
    from rich.syntax import Syntax
    
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    
    panel = Panel(
        syntax,
        title="Generated Code",
        border_style="green",
        padding=(1, 2)
    )
    
    console.print(panel)


def display_submission_result(success: bool, runtime: Optional[str] = None, memory: Optional[str] = None):
    """Display submission result with stats"""
    
    if success:
        result_text = Text()
        result_text.append("✅ SUBMISSION SUCCESSFUL!\n\n", style="bold green")
        
        if runtime:
            result_text.append(f"⚡ Runtime: {runtime}\n", style="cyan")
        if memory:
            result_text.append(f"💾 Memory: {memory}\n", style="cyan")
        
        panel = Panel(
            result_text,
            title="Result",
            border_style="green",
            padding=(1, 2)
        )
    else:
        result_text = Text()
        result_text.append("❌ SUBMISSION FAILED\n", style="bold red")
        
        panel = Panel(
            result_text,
            title="Result",
            border_style="red",
            padding=(1, 2)
        )
    
    console.print(panel)


def clear_screen():
    """Clear the console screen"""
    console.clear()


def pause():
    """Wait for user to press Enter"""
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def _load_config() -> Dict[str, str]:
    """Load ~/.leetagent/config.json if it exists."""
    config_path = settings.USER_CONFIG_PATH
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning(f"Failed to read config.json: {exc}")
        return {}


def _save_config(data: Dict[str, str]) -> None:
    """Persist config dictionary to ~/.leetagent/config.json."""
    config_path = settings.USER_CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _mask(value: Optional[str]) -> str:
    """Mask sensitive values, showing first/last 4 characters when possible."""
    if not value:
        return "—"
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}***{value[-4:]}"


def _get_env_value(key: str) -> Optional[str]:
    """Get value from environment variables."""
    return os.getenv(key) or None


def _get_keyring_value(key: str) -> Tuple[Optional[str], Optional[str]]:
    """Get value from OS keyring. Returns (value, error)."""
    try:
        import keyring  # type: ignore

        value = keyring.get_password(KEYRING_SERVICE, key)
        return value, None
    except ModuleNotFoundError:
        return None, "Install 'keyring' to use secret storage"
    except Exception as exc:
        return None, str(exc)


def _set_keyring_value(key: str, value: str) -> Optional[str]:
    """Store value in OS keyring. Returns error message if any."""
    try:
        import keyring  # type: ignore

        keyring.set_password(KEYRING_SERVICE, key, value)
        return None
    except ModuleNotFoundError:
        return "Python package 'keyring' is not installed. Install it with: pip install keyring"
    except Exception as exc:
        return str(exc)


def _resolve_credential(key: str) -> Tuple[Optional[str], str]:
    """Resolve credential value with priority: keyring -> config.json -> environment."""
    # Try keyring first
    value, err = _get_keyring_value(key)
    if value:
        return value, "keyring"
    
    # Try config.json
    config_data = _load_config()
    if key in config_data and config_data[key]:
        return config_data[key], "config.json"
    
    # Try environment
    env_value = _get_env_value(key)
    if env_value:
        return env_value, ".env/env"
    
    # Not found
    if err:
        return None, f"keyring error: {err}"
    return None, "missing"


def _credential_status_table() -> Table:
    """Create a table showing status of all credentials."""
    table = Table(
        title="Credential Sources",
        show_header=True,
        header_style="bold cyan",
        box=box.ROUNDED
    )
    table.add_column("Setting", style="yellow")
    table.add_column("Status", style="white")
    table.add_column("Source", style="cyan")
    table.add_column("Value", style="green")

    for key, label in CONFIG_KEYS.items():
        value, source = _resolve_credential(key)
        status = "✅" if value else "⚠"
        # Don't mask PREFERRED_LANGUAGE since it's not sensitive
        display_value = value if key == "PREFERRED_LANGUAGE" else _mask(value)
        table.add_row(label, status, source, display_value)

    return table


def print_credentials_help_rich():
    """Print the credentials help section using Rich formatting and colors."""
    body = Text()
    body.append("� Welcome to LeetAgent!\n\n", style="bold cyan")
    body.append("To get started, you need to configure your credentials:\n\n", style="white")
    
    body.append("1️⃣  Run the configuration wizard:\n", style="bold yellow")
    body.append("    ", style="white")
    body.append("leetagent config\n\n", style="bold green")
    
    body.append("2️⃣  Or set credentials manually:\n", style="bold yellow")
    body.append("    ", style="white")
    body.append("leetagent config-set GEMINI_API_KEY your_key_here\n", style="green")
    body.append("    ", style="white")
    body.append("leetagent config-set PREFERRED_LANGUAGE Python\n\n", style="green")
    
    body.append("3️⃣  After configuration, authenticate with LeetCode:\n", style="bold yellow")
    body.append("    ", style="white")
    body.append("leetagent login\n\n", style="green")
    
    body.append("💡 Quick Tips:\n", style="bold")
    body.append("  • Use ", style="white")
    body.append("leetagent config-show", style="cyan")
    body.append(" to view your settings\n", style="white")
    body.append("  • Use ", style="white")
    body.append("leetagent secret-set", style="cyan")
    body.append(" to store credentials in OS keyring (most secure)\n", style="white")
    body.append("  • All settings are stored in ", style="white")
    body.append("~/.leetagent/config.json\n\n", style="yellow")
    
    body.append("Ready to solve LeetCode problems with AI! 🎯", style="bold green")

    panel = Panel(body, border_style="cyan", title="Getting Started")
    console.print(panel)


@app.callback(invoke_without_command=True)
def first_run_banner(ctx: typer.Context):
    """Show one-time credentials guidance on first run, then defer to commands/help."""
    # Only show once per user by using a marker file
    try:
        marker_dir = settings.USER_DIR
        marker_dir.mkdir(parents=True, exist_ok=True)
        marker = marker_dir / ".first_run"
        if not marker.exists():
            # Print credentials guide before any other output (only once)
            print_credentials_help_rich()
            try:
                marker.write_text("shown", encoding="utf-8")
            except Exception:
                pass
    except Exception:
        # Non-fatal: never block CLI on banner problems
        pass
    # If no subcommand provided, show help afterwards
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command("login")
def login_command():
    """
    Interactive login command that opens LeetCode in browser,
    waits for manual login, and saves cookies automatically.
    
    Usage: leetagent login
    """
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from modules.auth import LeetCodeAuth
    from core.logger import logger
    
    console.clear()
    
    # Display header
    header = Panel(
        Text("🔐 LeetCode Login", style="bold cyan", justify="center"),
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(header)
    console.print()
    
    # Initialize auth module
    auth = LeetCodeAuth()
    
    # Check if cookies already exist
    if auth.cookies_exist():
        console.print("[yellow]⚠️  You're already logged in.[/yellow]")
        console.print(f"[dim]Cookies found at: {auth.get_cookie_path()}[/dim]\n")
        
        overwrite = Confirm.ask(
            "[bold]Would you like to overwrite existing cookies?[/bold]",
            default=False
        )
        
        if not overwrite:
            console.print("\n[cyan]✓ Login cancelled. Using existing cookies.[/cyan]")
            return
        
        console.print()
    
    # Status messages
    console.print("[bold cyan]🌐 Opening LeetCode Login Page...[/bold cyan]")
    console.print("[yellow]⚠️  Please log in manually and do not close the browser.[/yellow]\n")
    
    driver = None
    
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Initialize WebDriver
        with console.status("[bold cyan]Starting Chrome browser...[/bold cyan]"):
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        
        logger.info("Chrome WebDriver initialized for login")
        
        # Open LeetCode login page
        driver.get(f"{settings.LEETCODE_BASE_URL}/accounts/login/")
        
        console.print("[green]✓ Browser opened successfully![/green]")
        console.print(f"[dim]URL: {settings.LEETCODE_BASE_URL}/accounts/login/[/dim]\n")
        
        # Wait for user to login with real-time checking
        console.print("[bold]Please complete the following steps:[/bold]")
        console.print("  1. Log in to your LeetCode account")
        console.print("  2. Complete any verification if prompted")
        console.print("  3. Wait for the dashboard to load\n")
        
        # Poll for login completion (check every 2 seconds for up to 120 seconds)
        max_wait_time = 120  # 2 minutes
        check_interval = 2   # Check every 2 seconds
        checks = max_wait_time // check_interval
        
        logged_in = False
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[cyan]Waiting for login...",
                total=checks
            )
            
            for i in range(checks):
                time.sleep(check_interval)
                
                # Check if user logged in
                try:
                    current_url = driver.current_url
                    cookies = driver.get_cookies()
                    
                    # Look for LEETCODE_SESSION cookie with actual value
                    leetcode_session = next(
                        (c for c in cookies if c.get('name') == 'LEETCODE_SESSION'),
                        None
                    )
                    
                    # Check if logged in:
                    # 1. Has LEETCODE_SESSION cookie
                    # 2. Cookie has a value
                    # 3. Not on login page anymore
                    if (leetcode_session and 
                        leetcode_session.get('value') and 
                        len(leetcode_session.get('value', '')) > 10 and
                        '/accounts/login' not in current_url):
                        
                        logged_in = True
                        progress.update(task, completed=checks)
                        break
                        
                except Exception as e:
                    logger.debug(f"Login check error: {e}")
                
                progress.update(task, advance=1)
        
        console.print()
        
        # Verify login success
        if not logged_in:
            console.print("[red]❌ Login not detected![/red]")
            console.print("[yellow]⚠️  Please make sure you:[/yellow]")
            console.print("   • Actually logged in to your account")
            console.print("   • Completed any verification steps")
            console.print("   • Saw the LeetCode dashboard/homepage")
            console.print("\n[dim]Tip: The login page should redirect to leetcode.com after successful login[/dim]")
            logger.warning("Login failed: No valid session detected")
            return
        
        # Double-check we have the required cookies
        cookies = driver.get_cookies()
        has_session = any(
            cookie.get('name') == 'LEETCODE_SESSION' and 
            cookie.get('value') and 
            len(cookie.get('value', '')) > 10
            for cookie in cookies
        )
        
        if not has_session:
            console.print("[red]❌ No session cookies found![/red]")
            console.print("[yellow]⚠️  Please make sure you're logged in and try again.[/yellow]")
            logger.warning("Login failed: No session cookies detected")
            return
        
        # Show login verification info
        current_url = driver.current_url
        console.print("[green]✓ Login detected successfully![/green]")
        console.print(f"[dim]Current URL: {current_url}[/dim]")
        console.print(f"[dim]Found {len(cookies)} cookies[/dim]\n")
        
        # Extract and save cookies
        with console.status("[bold cyan]Saving cookies...[/bold cyan]"):
            success = auth.extract_and_save_cookies(driver)
        
        if success:
            console.print()
            success_panel = Panel(
                f"[green]✅ Login Successful! Cookies Saved.[/green]\n\n"
                f"[dim]Location: {auth.get_cookie_path()}[/dim]\n"
                f"[dim]Cookies: {len(cookies)} saved[/dim]",
                title="Success",
                border_style="green",
                padding=(1, 2)
            )
            console.print(success_panel)
            
            logger.info(f"Login successful, cookies saved to {auth.get_cookie_path()}")
        else:
            console.print("[red]❌ Failed to save cookies![/red]")
            logger.error("Failed to save cookies after login")
    
    except Exception as e:
        console.print(f"\n[red]❌ Error during login: {str(e)}[/red]")
        logger.error(f"Login command error: {e}")
    
    finally:
        # Close browser
        if driver:
            console.print("\n[dim]Closing browser...[/dim]")
            time.sleep(2)
            driver.quit()
            logger.info("Browser closed")
        
        console.print()


@app.command("logout")
def logout_command():
    """🚪 Logout (delete saved cookies)"""
    auth = LeetCodeAuth()
    if not auth.cookies_exist():
        console.print("[yellow]⚠️  You're not logged in.[/yellow]")
        return
    if not Confirm.ask("Delete saved cookies and logout?", default=False):
        console.print("[cyan]✓ Logout cancelled[/cyan]")
        return
    if auth.logout():
        console.print("[green]✅ Logged out. Cookies deleted.[/green]")
    else:
        console.print("[red]❌ Failed to delete cookies[/red]")


@app.command("session-status")
def session_status(check_online: bool = typer.Option(False, "--check-online", help="Verify API connectivity")):
    """🔍 Check credentials and session status"""
    console.print(Panel("[bold cyan]🔍 Credential & Session Status[/bold cyan]", border_style="cyan"))
    
    # Show credential status
    table = _credential_status_table()
    console.print(table)
    
    results = []
    
    # Optional online checks
    if check_online:
        gemini_key, _ = _resolve_credential("GEMINI_API_KEY")
        telegram_token, _ = _resolve_credential("TELEGRAM_TOKEN")
        chat_id, _ = _resolve_credential("CHAT_ID")
        
        gemini_status = "Skipped"
        telegram_status = "Skipped"
        
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                _ = next(iter(genai.list_models(page_size=1)), None)
                gemini_status = "✅ OK"
            except Exception as exc:
                gemini_status = f"⚠ {exc}"[:80]
        else:
            gemini_status = "⚠ Missing GEMINI_API_KEY"
        
        if telegram_token and chat_id:
            try:
                import requests
                resp = requests.get(
                    f"https://api.telegram.org/bot{telegram_token}/getMe",
                    timeout=5,
                )
                telegram_status = "✅ OK" if resp.ok else f"⚠ {resp.status_code}"
            except Exception as exc:
                telegram_status = f"⚠ {exc}"[:80]
        else:
            telegram_status = "⚠ Missing token/chat id"
        
        results.append(("Gemini API", gemini_status))
        results.append(("Telegram Bot", telegram_status))
    
    if results:
        net_table = Table(show_header=False, box=box.ROUNDED)
        for name, status in results:
            net_table.add_row(name, status)
        console.print(Panel(net_table, title="Online Checks", border_style="magenta"))
    
    # Show cookie status
    auth = LeetCodeAuth()
    cookies = auth.load_cookies() if auth.cookies_exist() else []
    cookie_panel = Panel(
        f"Cookies: {'✅ Loaded' if cookies else '⚠ Not found'}\nLocation: {auth.get_cookie_path()}",
        border_style="green" if cookies else "yellow"
    )
    console.print(cookie_panel)


@app.command("version")
def version_command():
    panel = Panel(
        f"[bold cyan]{settings.PROJECT_NAME}[/bold cyan]\n\n"
        f"[yellow]Version:[/yellow] {settings.VERSION}\n"
        f"[yellow]Author:[/yellow] {settings.AUTHOR}",
        title="About",
        border_style="cyan",
    )
    console.print(panel)


@app.command("update")
def update_command():
    """⬆️ Update LeetAgent to latest version"""
    console.print("[bold cyan]Updating leetagent...[/bold cyan]")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "leetagent"])
        console.print("[green]✅ Updated successfully[/green]")
    except Exception as e:
        console.print(f"[red]❌ Update failed: {e}[/red]")


@app.command("config", help="Interactive configuration wizard")
def config_command():
    """
    🎯 Interactive Configuration Wizard
    
    Set up your LeetAgent credentials and preferences through an easy-to-use wizard.
    All settings are stored securely in ~/.leetagent/config.json
    """
    console.print("\n")
    console.print(Panel(
        "[bold cyan]🚀 LeetAgent Configuration Wizard[/bold cyan]\n\n"
        "Let's set up your credentials and preferences.\n"
        "All values are stored locally in [yellow]~/.leetagent/config.json[/yellow]",
        border_style="cyan",
        padding=(1, 2)
    ))
    
    # Load existing config
    data = _load_config()
    
    # 1. Gemini API Key
    console.print("\n[bold]1️⃣  Gemini API Key[/bold]")
    console.print("[dim]Required for AI-powered code generation[/dim]")
    current = data.get("GEMINI_API_KEY", "")
    if current:
        console.print(f"[green]Current: {_mask(current)}[/green]")
        if not Confirm.ask("Update this value?", default=False):
            console.print("[dim]Keeping existing value[/dim]")
        else:
            current = ""
    
    if not current:
        console.print("[dim]💡 Tip: You can paste your API key here[/dim]")
        gemini_key = Prompt.ask("Enter your Gemini API Key")
        if gemini_key.strip():
            data["GEMINI_API_KEY"] = gemini_key.strip()
            console.print("[green]✅ Gemini API Key saved[/green]")
    
    # 2. Preferred Language
    console.print("\n[bold]2️⃣  Preferred Coding Language[/bold]")
    console.print("[dim]The language you want AI to generate solutions in[/dim]")
    current_lang = data.get("PREFERRED_LANGUAGE", "")
    if current_lang:
        console.print(f"[green]Current: {current_lang}[/green]")
        if not Confirm.ask("Update this value?", default=False):
            console.print("[dim]Keeping existing value[/dim]")
        else:
            current_lang = ""
    
    if not current_lang:
        console.print("[cyan]Supported languages:[/cyan]")
        for i, lang in enumerate(SUPPORTED_LANGUAGES, 1):
            console.print(f"  {i}. {lang}")
        
        lang_choice = Prompt.ask(
            "\nEnter language name or number",
            default="Python"
        )
        
        # Handle numeric input
        if lang_choice.isdigit():
            idx = int(lang_choice) - 1
            if 0 <= idx < len(SUPPORTED_LANGUAGES):
                lang_choice = SUPPORTED_LANGUAGES[idx]
        
        # Validate language
        matched = next((l for l in SUPPORTED_LANGUAGES if l.lower() == lang_choice.lower()), None)
        if matched:
            data["PREFERRED_LANGUAGE"] = matched
            console.print(f"[green]✅ Preferred language set to {matched}[/green]")
        else:
            console.print(f"[yellow]⚠ '{lang_choice}' not in supported list, but saving anyway[/yellow]")
            data["PREFERRED_LANGUAGE"] = lang_choice
    
    # 3. Telegram (Optional)
    console.print("\n[bold]3️⃣  Telegram Notifications (Optional)[/bold]")
    console.print("[dim]Get notified when solutions are submitted[/dim]")
    
    if not Confirm.ask("Configure Telegram notifications?", default=False):
        console.print("[dim]Skipping Telegram setup[/dim]")
    else:
        # Bot Token
        current_token = data.get("TELEGRAM_TOKEN", "")
        if current_token:
            console.print(f"[green]Current Bot Token: {_mask(current_token)}[/green]")
            if not Confirm.ask("Update Bot Token?", default=False):
                console.print("[dim]Keeping existing token[/dim]")
            else:
                current_token = ""
        
        if not current_token:
            console.print("[dim]💡 Tip: You can paste your bot token here[/dim]")
            bot_token = Prompt.ask("Enter Telegram Bot Token")
            if bot_token.strip():
                data["TELEGRAM_TOKEN"] = bot_token.strip()
                console.print("[green]✅ Bot Token saved[/green]")
        
        # Chat ID
        current_chat = data.get("CHAT_ID", "")
        if current_chat:
            console.print(f"[green]Current Chat ID: {_mask(current_chat)}[/green]")
            if not Confirm.ask("Update Chat ID?", default=False):
                console.print("[dim]Keeping existing Chat ID[/dim]")
            else:
                current_chat = ""
        
        if not current_chat:
            chat_id = Prompt.ask("Enter Telegram Chat ID")
            if chat_id.strip():
                data["CHAT_ID"] = chat_id.strip()
                console.print("[green]✅ Chat ID saved[/green]")
    
    # Save configuration
    try:
        _save_config(data)
        console.print("\n")
        console.print(Panel(
            "[bold green]🎉 Configuration Complete![/bold green]\n\n"
            f"[dim]Config saved to:[/dim] [yellow]{settings.USER_CONFIG_PATH}[/yellow]\n\n"
            "[dim]Next steps:[/dim]\n"
            "  • Run [cyan]leetagent login[/cyan] to authenticate with LeetCode\n"
            "  • Run [cyan]leetagent auto[/cyan] to solve today's challenge\n"
            "  • Run [cyan]leetagent config-show[/cyan] to view your settings",
            border_style="green",
            padding=(1, 2)
        ))
    except Exception as exc:
        console.print(Panel(
            f"[red]❌ Failed to save configuration:[/red]\n\n{exc}",
            border_style="red"
        ))
        raise typer.Exit(code=1)


@app.command("setup", help="First-time setup wizard (alias for config)")
def setup_command():
    """🎯 First-time setup wizard - same as 'leetagent config'"""
    config_command()


@app.command("config-set")
def config_set(
    key: str = typer.Argument(..., help="Config key (GEMINI_API_KEY, TELEGRAM_TOKEN, CHAT_ID, PREFERRED_LANGUAGE)"),
    value: str = typer.Argument(..., help="Value to store")
):
    """💾 Store a credential or setting in ~/.leetagent/config.json"""
    key_upper = key.strip().upper()
    
    if key_upper not in CONFIG_KEYS:
        console.print(Panel(
            f"[red]Unsupported key:[/red] {key}\n\n"
            f"[dim]Supported keys:[/dim]\n"
            f"  • {', '.join(CONFIG_KEYS.keys())}",
            border_style="red"
        ))
        raise typer.Exit(code=1)
    
    # Validate language if setting PREFERRED_LANGUAGE
    if key_upper == "PREFERRED_LANGUAGE":
        matched = next((l for l in SUPPORTED_LANGUAGES if l.lower() == value.strip().lower()), None)
        if matched:
            value = matched  # Use proper casing
        else:
            console.print(f"[yellow]⚠ Warning: '{value}' is not in the standard language list[/yellow]")
            console.print(f"[dim]Supported: {', '.join(SUPPORTED_LANGUAGES)}[/dim]")
            if not Confirm.ask("Save anyway?", default=True):
                raise typer.Exit(code=0)
    
    data = _load_config()
    data[key_upper] = value.strip()
    
    try:
        _save_config(data)
        console.print(Panel(
            f"[green]✅ Saved {CONFIG_KEYS[key_upper]}[/green]\n\n"
            f"[dim]Location:[/dim] [yellow]{settings.USER_CONFIG_PATH}[/yellow]",
            border_style="green"
        ))
    except Exception as exc:
        console.print(Panel(f"[red]❌ Failed to save config:[/red] {exc}", border_style="red"))
        raise typer.Exit(code=1)


@app.command("config-show")
def config_show():
    """👁 Display resolved configuration (with masking)"""
    table = _credential_status_table()
    panel = Panel(table, title="Current Configuration", border_style="cyan")
    console.print(panel)
    
    config_path = settings.USER_CONFIG_PATH
    if config_path.exists():
        console.print(f"\n[dim]Config file: {config_path}[/dim]")
    else:
        console.print("\n[yellow]No config file found. Values are loaded from keyring or environment.[/yellow]")


@app.command("secret-set")
def secret_set(
    key: str = typer.Argument(..., help="Secret key (GEMINI_API_KEY, TELEGRAM_TOKEN, CHAT_ID)")
):
    """🔐 Securely store a credential in OS keyring"""
    key_upper = key.strip().upper()
    
    # Only allow secret keys (not PREFERRED_LANGUAGE)
    secret_keys = {k: v for k, v in CONFIG_KEYS.items() if k != "PREFERRED_LANGUAGE"}
    
    if key_upper not in secret_keys:
        console.print(Panel(
            f"[red]Unsupported key:[/red] {key}\n\n"
            f"[dim]Supported secret keys:[/dim]\n"
            f"  • {', '.join(secret_keys.keys())}",
            border_style="red"
        ))
        raise typer.Exit(code=1)
    
    value = typer.prompt(
        f"Enter value for {CONFIG_KEYS[key_upper]}",
        hide_input=True,
        confirmation_prompt=True
    )
    
    if not value.strip():
        console.print("[red]❌ Value cannot be empty.[/red]")
        raise typer.Exit(code=1)
    
    error = _set_keyring_value(key_upper, value.strip())
    if error:
        console.print(Panel(f"[red]❌ Failed to store secret:[/red]\n\n{error}", border_style="red"))
        raise typer.Exit(code=1)
    
    console.print(Panel(
        f"[green]✅ Stored {CONFIG_KEYS[key_upper]} securely[/green]\n\n"
        f"[dim]Service:[/dim] {KEYRING_SERVICE}\n"
        f"[dim]Key:[/dim] {key_upper}",
        border_style="green"
    ))


@app.command("auto")
def auto_command():
    """🚀 Auto mode - solve today's daily challenge"""
    try:
        settings.validate()
    except Exception as e:
        console.print(f"[red]Config error:[/red] {e}\n[dim]Set GEMINI_API_KEY in your environment or .env[/dim]")
        raise typer.Exit(code=1)
    from main import main_auto
    exit_code = main_auto()
    raise typer.Exit(code=exit_code)


@app.command("direct")
def direct_command(
    url: str = typer.Argument(..., help="LeetCode problem URL"),
    language: str = typer.Option(None, "--language", "-l", help="Language (defaults to configured PREFERRED_LANGUAGE)")
):
    """🎯 Solve a specific problem directly"""
    try:
        settings.validate()
    except Exception as e:
        console.print(f"[red]Config error:[/red] {e}\n[dim]Run 'leetagent config' to set up credentials[/dim]")
        raise typer.Exit(code=1)
    
    # Use configured language if not specified
    if language is None:
        language = settings.PREFERRED_LANGUAGE
        console.print(f"[dim]Using configured language: {language}[/dim]")
    
    from main import main_direct
    exit_code = main_direct(url, language)
    raise typer.Exit(code=exit_code)


@app.command("interactive")
def interactive_command():
    """🎮 Enhanced interactive menu"""
    from modules import LeetCodeScraper, GeminiSolutionGenerator, CodeFormatter
    clear_screen()
    display_welcome()
    scraper = LeetCodeScraper()
    generator = GeminiSolutionGenerator()
    formatter = CodeFormatter()

    while True:
        display_menu()
        choice = Prompt.ask("\n[bold]Enter choice[/bold]", choices=["1","2","3","4","5"], default="1")
        if choice == "1":
            # Today's challenge
            problem = scraper.get_problem_metadata()
            if not problem:
                display_error("Failed to fetch today's challenge")
                continue
            display_problem_info(problem)
            lang = prompt_language()
            console.print("\n[bold cyan]Generating brute-force and optimized solutions...[/bold cyan]")
            brute = generator.generate_solution(problem=problem, language=lang, feedback="Provide a clear brute-force baseline solution with comments.", attempt_num=1)
            optimal = generator.generate_solution(problem=problem, language=lang, feedback="Provide an optimized solution with time/space analysis and comments.", attempt_num=2)
            # Show side-by-side
            from rich.columns import Columns
            b_syn = Panel(brute or "No output", title="Brute Force", border_style="yellow")
            o_syn = Panel(optimal or "No output", title="Optimized", border_style="green")
            console.print(Columns([b_syn, o_syn]))
            if Confirm.ask("Submit now?", default=False):
                from main import main_direct
                main_direct(problem.get('link') or problem.get('url') or problem.get('problem_url'), lang)
        elif choice == "2":
            url = prompt_problem_url()
            lang = prompt_language()
            from main import main_direct
            main_direct(url, lang)
        elif choice == "3":
            diff = Prompt.ask("Select difficulty", choices=["Easy","Medium","Hard"], default="Easy")
            console.print(f"[yellow]Difficulty filter '{diff}' not fully implemented yet. Use option 2 with a URL.[/yellow]")
        elif choice == "4":
            # Streak stats
            hist = settings.HISTORY_PATH
            if hist.exists():
                try:
                    import json
                    data = json.loads(hist.read_text(encoding='utf-8'))
                    total = len(data.get("solved", []))
                except Exception:
                    total = 0
            else:
                total = 0
            console.print(Panel(f"[bold green]🔥 Problems solved:[/bold green] {total}", border_style="green"))
        else:
            display_success("Goodbye! 👋")
            break


# Keep helper functions below. App is exported for setup entry point.
