"""
ACP (Agent Client Protocol) server for IDE integration.
Allows Alprina to be used as an IDE agent.
"""

from typing import Any, Dict
from rich.console import Console

console = Console()


def run_acp():
    """
    Start Alprina in ACP mode for IDE integration.
    """
    console.print("[cyan]Starting ACP server...[/cyan]")

    try:
        from agent_client_protocol import ACPServer, models

        class AlprinaACPServer(ACPServer):
            """Alprina ACP Server implementation."""

            async def handle_request(self, req: models.Request) -> models.Response:
                """Handle incoming ACP requests from IDE."""
                method = req.method
                params = req.params or {}

                console.print(f"[dim]ACP Request: {method}[/dim]")

                try:
                    if method == "scan":
                        result = await self._handle_scan(params)
                        return models.Response.ok(req.id, result)

                    elif method == "recon":
                        result = await self._handle_recon(params)
                        return models.Response.ok(req.id, result)

                    elif method == "mitigate":
                        result = await self._handle_mitigate(params)
                        return models.Response.ok(req.id, result)

                    elif method == "analyze_file":
                        result = await self._handle_analyze_file(params)
                        return models.Response.ok(req.id, result)

                    else:
                        return models.Response.error(
                            req.id,
                            -32601,
                            f"Method not found: {method}"
                        )

                except Exception as e:
                    console.print(f"[red]Error handling request: {e}[/red]")
                    return models.Response.error(
                        req.id,
                        -32603,
                        f"Internal error: {str(e)}"
                    )

            async def _handle_scan(self, params: Dict[str, Any]) -> Dict[str, Any]:
                """Handle scan request."""
                target = params.get("target")
                profile = params.get("profile", "default")
                safe_only = params.get("safe_only", True)

                if not target:
                    raise ValueError("Target parameter is required")

                from .security_engine import run_local_scan, run_remote_scan
                from pathlib import Path

                # Determine if local or remote
                target_path = Path(target)
                if target_path.exists():
                    result = run_local_scan(target, profile, safe_only)
                else:
                    result = run_remote_scan(target, profile, safe_only)

                return result

            async def _handle_recon(self, params: Dict[str, Any]) -> Dict[str, Any]:
                """Handle recon request."""
                target = params.get("target")
                passive = params.get("passive", True)

                if not target:
                    raise ValueError("Target parameter is required")

                from .security_engine import run_agent

                result = run_agent(
                    task="web-recon",
                    input_data=target,
                    metadata={"passive": passive}
                )

                return result

            async def _handle_mitigate(self, params: Dict[str, Any]) -> Dict[str, Any]:
                """Handle mitigation request."""
                finding = params.get("finding")

                if not finding:
                    raise ValueError("Finding parameter is required")

                from .security_engine import run_agent

                mitigation_prompt = f"""
                Security Finding: {finding.get('description')}
                Type: {finding.get('type')}
                Severity: {finding.get('severity')}

                Provide step-by-step mitigation guidance.
                """

                result = run_agent(
                    task="mitigation",
                    input_data=mitigation_prompt,
                    metadata=finding
                )

                return result

            async def _handle_analyze_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
                """Handle file analysis request."""
                file_path = params.get("file_path")
                content = params.get("content")

                if not file_path and not content:
                    raise ValueError("Either file_path or content is required")

                from pathlib import Path
                from .security_engine import run_agent

                if file_path:
                    content = Path(file_path).read_text()

                result = run_agent(
                    task="code-audit",
                    input_data=content,
                    metadata={"file": file_path}
                )

                return result

        # Start the ACP server with stdio transport
        server = AlprinaACPServer(transport="stdio")
        console.print("[green]ACP server started on stdio[/green]")
        server.serve()

    except ImportError:
        console.print("[red]agent-client-protocol not installed[/red]")
        console.print("[yellow]Install with: pip install agent-client-protocol[/yellow]")
    except Exception as e:
        console.print(f"[red]Failed to start ACP server: {e}[/red]")
