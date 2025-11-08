"""
Interactive CLI Mode

Provides a REPL-style interface for the Alprina CLI with:
- Rich output formatting (colors, tables, syntax highlighting)
- Progress indicators for long-running operations
- Auto-completion and command history
- Context-aware help

Context Engineering:
- Beautiful output doesn't inflate context
- Progress updates keep user informed
- Interactive mode for exploration
"""

import sys
import asyncio
from typing import Optional, List, Dict, Any
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich import print as rprint
from rich.tree import Tree
from loguru import logger

from alprina_cli.auth_system import get_auth_service, get_authz_service, Role
from alprina_cli.tools import ALL_TOOLS


class AlprinaInteractiveCLI:
    """
    Interactive REPL for Alprina CLI.

    Features:
    - Command auto-completion
    - Rich output formatting
    - Progress indicators
    - Command history
    - Context-aware help
    """

    def __init__(self):
        self.console = Console()
        self.auth_service = get_auth_service()
        self.authz_service = get_authz_service()
        self.current_user = None
        self.api_key = None

        # Available commands
        self.commands = {
            "help": self.cmd_help,
            "login": self.cmd_login,
            "logout": self.cmd_logout,
            "whoami": self.cmd_whoami,
            "tools": self.cmd_tools,
            "scan": self.cmd_scan,
            "recon": self.cmd_recon,
            "vuln-scan": self.cmd_vuln_scan,
            "history": self.cmd_history,
            "clear": self.cmd_clear,
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
        }

        # Setup prompt with auto-completion
        self.completer = WordCompleter(list(self.commands.keys()), ignore_case=True)

        # Setup custom style
        self.style = Style.from_dict({
            'prompt': '#00aa00 bold',
            'command': '#00aaff bold',
        })

        # Command history
        try:
            self.history = FileHistory('.alprina_history')
        except Exception:
            self.history = None

        self.session = PromptSession(
            completer=self.completer,
            style=self.style,
            history=self.history
        )

    def show_banner(self):
        """Display welcome banner"""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                            ║
║   █████╗ ██╗     ██████╗ ██████╗ ██╗███╗   ██╗ █████╗    ║
║  ██╔══██╗██║     ██╔══██╗██╔══██╗██║████╗  ██║██╔══██╗   ║
║  ███████║██║     ██████╔╝██████╔╝██║██╔██╗ ██║███████║   ║
║  ██╔══██║██║     ██╔═══╝ ██╔══██╗██║██║╚██╗██║██╔══██║   ║
║  ██║  ██║███████╗██║     ██║  ██║██║██║ ╚████║██║  ██║   ║
║  ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝   ║
║                                                            ║
║      Security Automation Platform - Interactive Mode      ║
║                    Type 'help' to start                    ║
║                                                            ║
╚═══════════════════════════════════════════════════════════╝
        """
        self.console.print(banner, style="bold cyan")

    def get_prompt(self) -> str:
        """Get the command prompt string"""
        if self.current_user:
            username = self.current_user.username
            role = self.current_user.role.value
            return f"[bold green]alprina[/bold green] [{role}@{username}]> "
        return "[bold green]alprina[/bold green] [guest]> "

    async def cmd_help(self, args: List[str]):
        """Show help information"""
        if args and args[0] in self.commands:
            # Show help for specific command
            cmd = args[0]
            self.console.print(f"\n[bold cyan]Help for '{cmd}':[/bold cyan]\n")
            # TODO: Add detailed help for each command
            self.console.print(f"Command: {cmd}")
        else:
            # Show general help
            table = Table(title="Available Commands", show_header=True, header_style="bold magenta")
            table.add_column("Command", style="cyan", no_wrap=True)
            table.add_column("Description")

            table.add_row("help [command]", "Show this help or help for a specific command")
            table.add_row("login", "Authenticate with API key")
            table.add_row("logout", "Log out current user")
            table.add_row("whoami", "Show current user information")
            table.add_row("tools", "List available security tools")
            table.add_row("scan <target>", "Perform security scan")
            table.add_row("recon <target>", "Perform reconnaissance")
            table.add_row("vuln-scan <target>", "Perform vulnerability scan")
            table.add_row("history", "Show command history")
            table.add_row("clear", "Clear screen")
            table.add_row("exit/quit", "Exit interactive mode")

            self.console.print(table)

    async def cmd_login(self, args: List[str]):
        """Authenticate user"""
        if self.current_user:
            self.console.print("[yellow]Already logged in. Use 'logout' first.[/yellow]")
            return

        if not args:
            # Interactive login
            from prompt_toolkit import prompt
            api_key = prompt("API Key: ", is_password=True)
        else:
            api_key = args[0]

        # Authenticate
        with self.console.status("[bold green]Authenticating...", spinner="dots"):
            user = self.auth_service.authenticate(api_key)

        if user:
            self.current_user = user
            self.api_key = api_key

            # Show success message
            panel = Panel(
                f"[bold green]✓[/bold green] Authenticated as [cyan]{user.username}[/cyan]\n"
                f"Role: [yellow]{user.role.value}[/yellow]\n"
                f"Email: {user.email}",
                title="[bold green]Login Successful[/bold green]",
                border_style="green"
            )
            self.console.print(panel)
        else:
            self.console.print("[bold red]✗ Authentication failed. Invalid API key.[/bold red]")

    async def cmd_logout(self, args: List[str]):
        """Log out current user"""
        if not self.current_user:
            self.console.print("[yellow]Not logged in.[/yellow]")
            return

        username = self.current_user.username
        self.current_user = None
        self.api_key = None

        self.console.print(f"[green]Logged out {username}[/green]")

    async def cmd_whoami(self, args: List[str]):
        """Show current user information"""
        if not self.current_user:
            self.console.print("[yellow]Not logged in. Use 'login' to authenticate.[/yellow]")
            return

        user = self.current_user

        # Get user permissions
        permissions = self.authz_service.get_user_permissions(user)

        # Create info panel
        table = Table(show_header=False, box=None)
        table.add_column("Field", style="cyan bold")
        table.add_column("Value")

        table.add_row("Username", user.username)
        table.add_row("Email", user.email)
        table.add_row("Role", user.role.value)
        table.add_row("User ID", user.user_id)
        table.add_row("Active", "✓ Yes" if user.is_active else "✗ No")
        table.add_row("Permissions", f"{len(permissions)} permissions")

        panel = Panel(table, title="[bold cyan]Current User[/bold cyan]", border_style="cyan")
        self.console.print(panel)

        # Show permissions
        if permissions:
            perm_tree = Tree("[bold cyan]Permissions[/bold cyan]")
            for perm in permissions:
                perm_tree.add(f"[green]✓[/green] {perm.value}")
            self.console.print(perm_tree)

    async def cmd_tools(self, args: List[str]):
        """List available security tools"""
        table = Table(title="Available Security Tools", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Tool Name", style="cyan")
        table.add_column("Description")
        table.add_column("Access", justify="center")

        for i, tool in enumerate(ALL_TOOLS, 1):
            # Check if user has access
            if self.current_user:
                has_access = self.authz_service.can_use_tool(self.current_user, tool.__class__.__name__)
                access_indicator = "[green]✓[/green]" if has_access else "[red]✗[/red]"
            else:
                access_indicator = "[dim]?[/dim]"

            table.add_row(
                str(i),
                tool.name,
                tool.description,
                access_indicator
            )

        self.console.print(table)

        if not self.current_user:
            self.console.print("\n[dim]Login to see your tool access permissions[/dim]")

    async def cmd_scan(self, args: List[str]):
        """Perform security scan"""
        if not self.current_user:
            self.console.print("[yellow]Please login first using 'login' command[/yellow]")
            return

        if not args:
            self.console.print("[yellow]Usage: scan <target> [ports][/yellow]")
            return

        target = args[0]
        ports = args[1] if len(args) > 1 else "80,443"

        # Check authorization
        if not self.authz_service.can_use_tool(self.current_user, "ScanTool"):
            self.console.print("[bold red]✗ Permission denied. You don't have access to ScanTool.[/bold red]")
            return

        # Import and execute tool
        from alprina_cli.tools.security.scan import ScanTool, ScanParams

        tool = ScanTool()
        params = ScanParams(target=target, scan_type="quick", ports=ports)

        # Show progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task(f"[cyan]Scanning {target}...", total=None)

            # Execute scan
            result = await tool(params)

            progress.update(task, completed=True)

        # Display results
        if hasattr(result, 'content'):
            self.display_scan_results(target, result.content)
        else:
            self.console.print(f"[red]Scan failed: {result.message}[/red]")

    async def cmd_recon(self, args: List[str]):
        """Perform reconnaissance"""
        if not self.current_user:
            self.console.print("[yellow]Please login first[/yellow]")
            return

        if not args:
            self.console.print("[yellow]Usage: recon <target> [operation][/yellow]")
            return

        target = args[0]
        operation = args[1] if len(args) > 1 else "whois"

        # Import and execute
        from alprina_cli.tools.security.recon import ReconTool, ReconParams

        tool = ReconTool()
        params = ReconParams(target=target, operation=operation, timeout=30)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(f"[cyan]Reconnaissance on {target}...", total=None)
            result = await tool(params)
            progress.update(task, completed=True)

        # Display results
        if hasattr(result, 'content'):
            panel = Panel(
                str(result.content),
                title=f"[bold cyan]Recon Results: {target}[/bold cyan]",
                border_style="cyan"
            )
            self.console.print(panel)
        else:
            self.console.print(f"[red]Recon failed: {result.message}[/red]")

    async def cmd_vuln_scan(self, args: List[str]):
        """Perform vulnerability scan"""
        if not self.current_user:
            self.console.print("[yellow]Please login first[/yellow]")
            return

        if not args:
            self.console.print("[yellow]Usage: vuln-scan <target>[/yellow]")
            return

        target = args[0]

        # Import and execute
        from alprina_cli.tools.security.vuln_scan import VulnScanTool, VulnScanParams

        tool = VulnScanTool()
        params = VulnScanParams(target=target, scan_type="web", depth="basic")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task(f"[cyan]Vulnerability scanning {target}...", total=None)
            result = await tool(params)
            progress.update(task, completed=True)

        # Display results
        if hasattr(result, 'content'):
            self.display_vuln_results(target, result.content)
        else:
            self.console.print(f"[red]Vulnerability scan failed: {result.message}[/red]")

    def display_scan_results(self, target: str, results: Any):
        """Display scan results in a formatted table"""
        if isinstance(results, dict):
            table = Table(title=f"Scan Results: {target}", show_header=True, header_style="bold magenta")
            table.add_column("Property", style="cyan")
            table.add_column("Value")

            for key, value in results.items():
                table.add_row(str(key), str(value))

            self.console.print(table)
        else:
            panel = Panel(
                str(results),
                title=f"[bold cyan]Scan Results: {target}[/bold cyan]",
                border_style="cyan"
            )
            self.console.print(panel)

    def display_vuln_results(self, target: str, results: Any):
        """Display vulnerability scan results"""
        if isinstance(results, dict) and 'findings' in results:
            findings = results.get('findings', [])

            table = Table(title=f"Vulnerabilities Found: {target}", show_header=True, header_style="bold red")
            table.add_column("#", style="dim", width=4)
            table.add_column("Severity", style="bold")
            table.add_column("Title")
            table.add_column("Description")

            for i, finding in enumerate(findings, 1):
                severity = finding.get('severity', 'UNKNOWN')
                severity_style = {
                    'CRITICAL': '[bold red]CRITICAL[/bold red]',
                    'HIGH': '[red]HIGH[/red]',
                    'MEDIUM': '[yellow]MEDIUM[/yellow]',
                    'LOW': '[blue]LOW[/blue]',
                    'INFO': '[dim]INFO[/dim]'
                }.get(severity, severity)

                table.add_row(
                    str(i),
                    severity_style,
                    finding.get('title', 'N/A'),
                    finding.get('description', 'N/A')[:50] + "..."
                )

            self.console.print(table)
        else:
            self.display_scan_results(target, results)

    async def cmd_history(self, args: List[str]):
        """Show command history"""
        self.console.print("[dim]Command history feature coming soon...[/dim]")

    async def cmd_clear(self, args: List[str]):
        """Clear screen"""
        self.console.clear()

    async def cmd_exit(self, args: List[str]):
        """Exit interactive mode"""
        self.console.print("\n[cyan]Goodbye! Stay secure. 🔒[/cyan]\n")
        sys.exit(0)

    async def execute_command(self, command_line: str):
        """Execute a command"""
        if not command_line.strip():
            return

        parts = command_line.strip().split()
        command = parts[0].lower()
        args = parts[1:]

        if command in self.commands:
            try:
                await self.commands[command](args)
            except Exception as e:
                self.console.print(f"[bold red]Error executing command: {e}[/bold red]")
                logger.error(f"Command execution error: {e}", exc_info=True)
        else:
            self.console.print(f"[yellow]Unknown command: {command}. Type 'help' for available commands.[/yellow]")

    async def run(self):
        """Run the interactive CLI"""
        self.show_banner()

        # Show login prompt if not authenticated
        if not self.current_user:
            self.console.print("\n[dim]Tip: Use 'login' to authenticate or 'help' to see available commands[/dim]\n")

        while True:
            try:
                # Get command from user
                command_line = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.session.prompt(self.get_prompt(), default="")
                )

                # Execute command
                await self.execute_command(command_line)

            except KeyboardInterrupt:
                self.console.print("\n[dim]Use 'exit' or 'quit' to exit[/dim]")
                continue
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"[bold red]Error: {e}[/bold red]")
                logger.error(f"Interactive CLI error: {e}", exc_info=True)


async def main():
    """Main entry point for interactive CLI"""
    cli = AlprinaInteractiveCLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())
