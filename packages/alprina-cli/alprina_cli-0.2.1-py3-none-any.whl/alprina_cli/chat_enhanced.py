"""
Interactive chat interface for Alprina.
Provides conversational AI assistant for security scanning.
"""

from typing import Optional
from pathlib import Path
import re
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.key_binding import KeyBindings
from loguru import logger

from .context_manager import ConversationContext
from .llm_provider import get_llm_client
from .scanner import scan_command
from .mitigation import mitigate_command

console = Console()


class AlprinaChatSession:
    """Interactive chat session with Alprina AI."""

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        streaming: bool = True,
        context_file: Optional[Path] = None
    ):
        """
        Initialize chat session.

        Args:
            model: LLM model to use
            streaming: Enable streaming responses
            context_file: Load previous scan context
        """
        self.model = model
        self.streaming = streaming
        self.context = ConversationContext()
        self.llm = get_llm_client(model=model)

        # Set up prompt session with history
        history_file = Path.home() / '.alprina' / 'chat_history.txt'
        history_file.parent.mkdir(parents=True, exist_ok=True)

        self.session = PromptSession(
            history=FileHistory(str(history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            key_bindings=self._create_key_bindings()
        )

        # Load context if provided
        if context_file:
            self.context.load_scan_results(context_file)

        logger.info(f"Chat session initialized with model: {model}")

    def _create_key_bindings(self):
        """Create custom key bindings."""
        kb = KeyBindings()

        @kb.add('c-c')
        def _(event):
            """Handle Ctrl+C gracefully."""
            event.app.exit()

        return kb

    def start(self):
        """Start interactive chat loop."""
        self._show_welcome()

        while True:
            try:
                # Get user input
                user_input = self.session.prompt("\n[bold green]You:[/bold green] ")

                if not user_input.strip():
                    continue

                # Check for exit
                if user_input.lower() in ['exit', 'quit', 'q', 'bye']:
                    self._handle_exit()
                    break

                # Handle special commands
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                    continue

                # Process as chat message
                self._process_message(user_input)

            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' or Ctrl+D to quit[/yellow]")
                continue
            except EOFError:
                self._handle_exit()
                break
            except Exception as e:
                logger.error(f"Chat error: {e}", exc_info=True)
                console.print(f"[red]Error: {e}[/red]")

    def _show_welcome(self):
        """Show welcome message."""
        console.print(Panel(
            "[bold cyan]Alprina AI Security Assistant[/bold cyan]\n\n"
            "I can help you with:\n"
            "• Running security scans on code, APIs, and infrastructure\n"
            "• Explaining vulnerabilities and security findings\n"
            "• Providing remediation steps and code fixes\n"
            "• Answering security questions and best practices\n\n"
            "[dim]Type '/help' for commands or just ask me anything![/dim]\n"
            "[dim]Type 'exit' to quit[/dim]",
            title="🛡️  Alprina Chat",
            border_style="cyan"
        ))

        # Show context if loaded
        if self.context.scan_results:
            console.print(f"\n[cyan]📊 Context loaded:[/cyan] {self.context.get_context_summary()}\n")

    def _process_message(self, user_input: str):
        """
        Process user message and get AI response.

        Args:
            user_input: User's message
        """
        # Add to context
        self.context.add_user_message(user_input)

        # Check if user wants to scan something
        if self._is_scan_request(user_input):
            self._handle_scan_request(user_input)
            return

        # Check if user wants mitigation
        if self._is_mitigation_request(user_input):
            self._handle_mitigation_request(user_input)
            return

        # Get AI response
        console.print(f"\n[bold cyan]Alprina:[/bold cyan]")

        if self.streaming:
            response = self._get_streaming_response(user_input)
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                progress.add_task("Thinking...", total=None)
                response = self._get_response(user_input)

            console.print(Markdown(response))

        self.context.add_assistant_message(response)

    def _get_response(self, user_input: str) -> str:
        """
        Get AI response (non-streaming).

        Args:
            user_input: User's message

        Returns:
            AI response text
        """
        try:
            system_prompt = self._build_system_prompt()
            messages = self.context.get_messages_for_llm()

            response = self.llm.chat(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=4096,
                temperature=0.7
            )

            return response
        except Exception as e:
            logger.error(f"Failed to get AI response: {e}")
            return f"I encountered an error: {e}. Please try again."

    def _get_streaming_response(self, user_input: str) -> str:
        """
        Get AI response with streaming.

        Args:
            user_input: User's message

        Returns:
            Full AI response text
        """
        try:
            system_prompt = self._build_system_prompt()
            messages = self.context.get_messages_for_llm()

            full_response = ""
            for chunk in self.llm.chat_streaming(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=4096,
                temperature=0.7
            ):
                console.print(chunk, end="")
                full_response += chunk

            console.print()  # Newline after streaming
            return full_response

        except Exception as e:
            logger.error(f"Failed to get streaming response: {e}")
            return f"\n\nI encountered an error: {e}. Please try again."

    def _build_system_prompt(self) -> str:
        """
        Build context-aware system prompt.

        Returns:
            System prompt string
        """
        base_prompt = """You are Alprina, an AI-powered security assistant designed to help developers and security professionals.

Your capabilities:
- Analyzing security scan results and vulnerabilities
- Explaining security concepts and vulnerabilities in clear terms
- Providing actionable remediation steps and code fixes
- Answering questions about security best practices
- Guiding users through security assessments

Guidelines:
- Be concise but comprehensive in explanations
- Always prioritize security and ethical practices
- Provide code examples when relevant
- Use markdown formatting for better readability
- If you don't know something, admit it rather than guessing
- Focus on actionable insights, not just theory

Communication style:
- Professional but friendly
- Clear and jargon-free when possible
- Use examples to illustrate concepts
- Ask clarifying questions if needed"""

        # Add scan context if available
        if self.context.scan_results:
            context_info = self.context.get_detailed_context()
            base_prompt += f"\n\nCurrent Scan Context:\n{context_info}"

        return base_prompt

    def _is_scan_request(self, text: str) -> bool:
        """Check if user wants to run a scan."""
        scan_keywords = ['scan', 'analyze', 'check', 'test', 'audit']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in scan_keywords) and \
               ('my' in text_lower or './' in text or 'http' in text_lower or 'file' in text_lower)

    def _is_mitigation_request(self, text: str) -> bool:
        """Check if user wants mitigation steps."""
        mitigation_keywords = ['fix', 'remediate', 'solve', 'patch', 'how to fix']
        return any(keyword in text.lower() for keyword in mitigation_keywords)

    def _handle_scan_request(self, user_input: str):
        """Handle scan request from natural language."""
        # Try to extract target from user input
        target = self._extract_target(user_input)

        if not target:
            console.print("[yellow]I'd be happy to run a scan! What would you like me to scan?[/yellow]")
            console.print("[dim]Example: ./src, https://api.example.com, or /path/to/file[/dim]")
            return

        console.print(f"\n[cyan]→ Running security scan on:[/cyan] {target}\n")

        # Determine profile based on target
        profile = "code-audit" if Path(target).exists() else "web-recon"

        # Run scan (this will use the existing scan_command)
        try:
            scan_command(target, profile=profile, safe_only=True, output=None)

            # The scan results would be captured here
            # For now, simulate adding to context
            console.print(f"\n[green]✓ Scan complete![/green]")
            console.print("[dim]Type 'explain' to learn about findings or 'fix' for remediation steps[/dim]\n")

        except Exception as e:
            console.print(f"[red]Scan failed: {e}[/red]")
            logger.error(f"Scan failed: {e}", exc_info=True)

    def _handle_mitigation_request(self, user_input: str):
        """Handle mitigation request."""
        console.print("\n[cyan]→ Getting remediation suggestions...[/cyan]\n")

        try:
            # Run mitigation command
            mitigate_command(finding_id=None, report_file=None)

        except Exception as e:
            console.print(f"[red]Failed to get mitigation: {e}[/red]")
            logger.error(f"Mitigation failed: {e}", exc_info=True)

    def _extract_target(self, text: str) -> Optional[str]:
        """Extract scan target from natural language."""
        # Look for file paths
        file_pattern = r'\.\/[\w\/\-\.]+'
        match = re.search(file_pattern, text)
        if match:
            return match.group(0)

        # Look for URLs
        url_pattern = r'https?://[\w\-\.\/]+'
        match = re.search(url_pattern, text)
        if match:
            return match.group(0)

        # Look for absolute paths
        path_pattern = r'/[\w\/\-\.]+'
        match = re.search(path_pattern, text)
        if match:
            return match.group(0)

        return None

    def _handle_command(self, command: str):
        """
        Handle special chat commands.

        Args:
            command: Command string starting with /
        """
        cmd_parts = command.split()
        cmd_name = cmd_parts[0].lower()

        if cmd_name == '/help':
            self._show_help()
        elif cmd_name == '/scan':
            if len(cmd_parts) < 2:
                console.print("[yellow]Usage: /scan <target>[/yellow]")
            else:
                target = cmd_parts[1]
                self._handle_scan_request(f"scan {target}")
        elif cmd_name == '/explain':
            if len(cmd_parts) < 2:
                self._show_findings()
            else:
                finding_id = cmd_parts[1]
                self._explain_finding(finding_id)
        elif cmd_name == '/fix':
            if len(cmd_parts) < 2:
                console.print("[yellow]Usage: /fix <finding_id>[/yellow]")
            else:
                finding_id = cmd_parts[1]
                self._fix_finding(finding_id)
        elif cmd_name == '/report':
            self._show_report()
        elif cmd_name == '/clear':
            self.context.clear()
            console.print("[green]✓ Conversation history cleared[/green]")
        elif cmd_name == '/stats':
            self._show_stats()
        elif cmd_name == '/save':
            self._save_conversation()
        else:
            console.print(f"[red]Unknown command: {cmd_name}[/red]")
            console.print("[dim]Type /help for available commands[/dim]")

    def _show_help(self):
        """Show help message."""
        help_table = Table(title="Available Commands", show_header=True, header_style="bold cyan")
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description")

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

        console.print(help_table)

    def _show_findings(self):
        """Show current scan findings."""
        if not self.context.current_findings:
            console.print("[yellow]No scan findings available. Run a scan first![/yellow]")
            return

        findings_table = Table(title="Current Findings", show_header=True, header_style="bold")
        findings_table.add_column("ID", style="dim")
        findings_table.add_column("Severity")
        findings_table.add_column("Title")
        findings_table.add_column("File", style="dim")

        for finding in self.context.current_findings:
            severity_style = {
                'HIGH': 'bold red',
                'MEDIUM': 'bold yellow',
                'LOW': 'bold green'
            }.get(finding.get('severity', 'UNKNOWN'), 'white')

            findings_table.add_row(
                finding.get('id', 'N/A'),
                f"[{severity_style}]{finding.get('severity', 'UNKNOWN')}[/{severity_style}]",
                finding.get('title', 'Unknown'),
                finding.get('file', 'N/A')
            )

        console.print(findings_table)

    def _explain_finding(self, finding_id: str):
        """Explain specific finding."""
        finding = self.context.get_finding(finding_id)
        if not finding:
            console.print(f"[red]Finding {finding_id} not found[/red]")
            return

        # Use AI to explain the finding
        explanation_request = f"Can you explain this security finding in detail?\n\n{finding}"
        self._process_message(explanation_request)

    def _fix_finding(self, finding_id: str):
        """Get fix for specific finding."""
        finding = self.context.get_finding(finding_id)
        if not finding:
            console.print(f"[red]Finding {finding_id} not found[/red]")
            return

        # Use AI to provide fix
        fix_request = f"How can I fix this security vulnerability?\n\n{finding}"
        self._process_message(fix_request)

    def _show_report(self):
        """Show scan report summary."""
        if not self.context.scan_results:
            console.print("[yellow]No scan results available[/yellow]")
            return

        summary = self.context.get_context_summary()
        console.print(Panel(
            f"[bold]Scan Report[/bold]\n\n{summary}",
            border_style="cyan"
        ))

    def _show_stats(self):
        """Show conversation statistics."""
        stats = self.context.get_statistics()

        stats_table = Table(title="Session Statistics", show_header=False)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="bold")

        stats_table.add_row("Messages", str(stats['total_messages']))
        stats_table.add_row("  User", str(stats['user_messages']))
        stats_table.add_row("  Assistant", str(stats['assistant_messages']))
        stats_table.add_row("Findings", str(stats['total_findings']))
        stats_table.add_row("  HIGH", str(stats['high_severity']))
        stats_table.add_row("  MEDIUM", str(stats['medium_severity']))
        stats_table.add_row("  LOW", str(stats['low_severity']))
        stats_table.add_row("Duration", f"{stats['session_duration']:.0f}s")

        console.print(stats_table)

    def _save_conversation(self):
        """Save conversation to file."""
        output_file = Path.home() / '.alprina' / 'conversations' / f"chat_{self.context.session_start.strftime('%Y%m%d_%H%M%S')}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        self.context.save_conversation(output_file)
        console.print(f"[green]✓ Conversation saved to:[/green] {output_file}")

    def _handle_exit(self):
        """Handle exit gracefully."""
        stats = self.context.get_statistics()
        console.print(f"\n[cyan]Thanks for using Alprina![/cyan]")
        console.print(f"[dim]Session stats: {stats['total_messages']} messages, {stats['session_duration']:.0f}s duration[/dim]")
        console.print("[dim]💾 Use /save before exit to save your conversation[/dim]\n")


def chat_command(
    model: str = "claude-3-5-sonnet-20241022",
    streaming: bool = True,
    load_results: Optional[Path] = None
):
    """
    Start interactive chat session with Alprina AI.

    Args:
        model: LLM model to use
        streaming: Enable streaming responses
        load_results: Load previous scan results for context
    """
    try:
        session = AlprinaChatSession(
            model=model,
            streaming=streaming,
            context_file=load_results
        )
        session.start()
    except Exception as e:
        logger.error(f"Chat session error: {e}", exc_info=True)
        console.print(f"[red]Chat error: {e}[/red]")
        sys.exit(1)
