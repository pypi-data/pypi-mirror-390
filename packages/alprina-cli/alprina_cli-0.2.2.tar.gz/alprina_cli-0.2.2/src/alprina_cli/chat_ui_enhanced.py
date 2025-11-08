"""
Beautiful Kimi-style chat UI enhancements for Alprina.
"""

from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED
from rich.table import Table

console = Console()

# Alprina brand color
ALPRINA_RED = "#FF0420"


def show_beautiful_welcome():
    """Show beautiful ASCII art welcome with Alprina branding."""
    console.clear()

    # Beautiful ASCII art header
    header = Text()
    header.append("\n")
    header.append("   █████╗ ██╗     ██████╗ ██████╗ ██╗███╗   ██╗ █████╗ \n", style=f"bold {ALPRINA_RED}")
    header.append("  ██╔══██╗██║     ██╔══██╗██╔══██╗██║████╗  ██║██╔══██╗\n", style=f"bold {ALPRINA_RED}")
    header.append("  ███████║██║     ██████╔╝██████╔╝██║██╔██╗ ██║███████║\n", style=f"bold {ALPRINA_RED}")
    header.append("  ██╔══██║██║     ██╔═══╝ ██╔══██╗██║██║╚██╗██║██╔══██║\n", style=f"bold {ALPRINA_RED}")
    header.append("  ██║  ██║███████╗██║     ██║  ██║██║██║ ╚████║██║  ██║\n", style=f"bold {ALPRINA_RED}")
    header.append("  ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝\n", style=f"bold {ALPRINA_RED}")
    header.append("\n")
    header.append("  AI Security Assistant", style="dim")
    header.append(" • ", style="dim")
    header.append("Chat Mode", style=ALPRINA_RED)
    header.append("\n\n")

    console.print(header)

    # Capabilities in a beautiful box
    capabilities_panel = Panel(
        f"[white]I can help you with:[/white]\n\n"
        f"  [{ALPRINA_RED}]•[/{ALPRINA_RED}]  Running security scans on code, APIs, and infrastructure\n"
        f"  [{ALPRINA_RED}]•[/{ALPRINA_RED}]  Explaining vulnerabilities and security findings\n"
        f"  [{ALPRINA_RED}]•[/{ALPRINA_RED}]  Providing remediation steps and code fixes\n"
        f"  [{ALPRINA_RED}]•[/{ALPRINA_RED}]  Answering security questions and best practices\n\n"
        f"[dim]Type [bold]/help[/bold] for commands or just ask me anything!\n"
        f"Type [bold]exit[/bold] or press [bold]Ctrl+D[/bold] to quit[/dim]",
        border_style=ALPRINA_RED,
        box=ROUNDED,
        padding=(1, 2)
    )
    console.print(capabilities_panel)
    console.print()


def display_user_message(message: str):
    """Display user message in Kimi-style beautiful format."""
    timestamp = datetime.now().strftime("%H:%M")
    
    console.print()
    console.print(f"[dim]{timestamp}[/dim]  [bold white]You[/bold white]")
    
    # Create a subtle message bubble effect
    message_panel = Panel(
        f"[white]{message}[/white]",
        border_style="dim white",
        box=ROUNDED,
        padding=(0, 1),
        expand=False
    )
    console.print(message_panel)


def display_assistant_header():
    """Display assistant message header in Kimi style."""
    timestamp = datetime.now().strftime("%H:%M")
    console.print()
    console.print(f"[dim]{timestamp}[/dim]  [bold {ALPRINA_RED}]Alprina[/bold {ALPRINA_RED}]")


def display_thinking_indicator():
    """Show thinking indicator."""
    console.print(f"[dim {ALPRINA_RED}]● Thinking...[/dim {ALPRINA_RED}]")


def display_error(error_message: str):
    """Display error in beautiful format."""
    console.print()
    console.print(Panel(
        f"[red]✗ {error_message}[/red]",
        border_style="red",
        box=ROUNDED,
        padding=(0, 1)
    ))
    console.print()


def display_success(success_message: str):
    """Display success message."""
    console.print()
    console.print(Panel(
        f"[green]✓ {success_message}[/green]",
        border_style="green",
        box=ROUNDED,
        padding=(0, 1)
    ))
    console.print()


def display_info(info_message: str):
    """Display info message."""
    console.print()
    console.print(Panel(
        f"[{ALPRINA_RED}]→[/{ALPRINA_RED}] {info_message}",
        border_style=ALPRINA_RED,
        box=ROUNDED,
        padding=(0, 1)
    ))
    console.print()


def create_help_table():
    """Create beautiful help table."""
    help_table = Table(
        title=f"[bold {ALPRINA_RED}]Available Commands[/bold {ALPRINA_RED}]",
        show_header=True,
        header_style="bold white",
        border_style=ALPRINA_RED,
        box=ROUNDED,
        padding=(0, 1)
    )
    help_table.add_column("Command", style=ALPRINA_RED, no_wrap=True)
    help_table.add_column("Description", style="white")

    commands = [
        ("/help", "Show this help message"),
        ("/scan <target>", "Run security scan on target"),
        ("/explain [id]", "Explain finding (or list all)"),
        ("/fix <id>", "Get fix for specific finding"),
        ("/report", "Show current scan summary"),
        ("/clear", "Clear conversation history"),
        ("/stats", "Show conversation statistics"),
        ("/save", "Save conversation to file"),
        ("exit", "Exit chat session"),
    ]

    for cmd, desc in commands:
        help_table.add_row(cmd, desc)

    console.print()
    console.print(help_table)
    console.print()


def create_stats_table(stats: dict):
    """Create beautiful stats table."""
    stats_table = Table(
        title=f"[bold {ALPRINA_RED}]Session Statistics[/bold {ALPRINA_RED}]",
        show_header=False,
        border_style=ALPRINA_RED,
        box=ROUNDED,
        padding=(0, 1)
    )
    stats_table.add_column("Metric", style="white")
    stats_table.add_column("Value", style=f"bold {ALPRINA_RED}", justify="right")

    stats_table.add_row("Messages", str(stats.get('total_messages', 0)))
    stats_table.add_row("  └─ User", str(stats.get('user_messages', 0)))
    stats_table.add_row("  └─ Assistant", str(stats.get('assistant_messages', 0)))
    stats_table.add_row("Findings", str(stats.get('total_findings', 0)))
    stats_table.add_row("  └─ HIGH", str(stats.get('high_severity', 0)))
    stats_table.add_row("  └─ MEDIUM", str(stats.get('medium_severity', 0)))
    stats_table.add_row("  └─ LOW", str(stats.get('low_severity', 0)))
    stats_table.add_row("Duration", f"{stats.get('session_duration', 0):.0f}s")

    console.print()
    console.print(stats_table)
    console.print()


def display_goodbye(stats: dict):
    """Display beautiful goodbye message."""
    console.print()
    console.print(Panel(
        f"[bold {ALPRINA_RED}]Thanks for using Alprina![/bold {ALPRINA_RED}]\n\n"
        f"[white]Session Statistics:[/white]\n"
        f"  • {stats.get('total_messages', 0)} messages\n"
        f"  • {stats.get('session_duration', 0):.0f}s duration\n\n"
        f"[dim]💾 Use /save before exit to save your conversation[/dim]",
        border_style=ALPRINA_RED,
        box=ROUNDED,
        padding=(1, 2)
    ))
    console.print()
