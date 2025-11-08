"""
Alprina CLI Tools

Context-engineered tool system following Anthropic's best practices.

Tools vs Agents:
- Tools = Callable utilities with clear interfaces (lightweight)
- Agents = Full LLM instances with prompts (heavy)

We use tools for efficiency, composability, and context management.
"""

from alprina_cli.tools.base import (
    AlprinaToolBase,
    SyncToolBase,
    ToolResult,
    ToolOk,
    ToolError,
    TParams
)

# Import tools
from alprina_cli.tools.security.network_analyzer import NetworkAnalyzerTool
from alprina_cli.tools.security.scan import ScanTool
from alprina_cli.tools.security.recon import ReconTool
from alprina_cli.tools.security.vuln_scan import VulnScanTool
from alprina_cli.tools.security.exploit import ExploitTool
from alprina_cli.tools.security.red_team import RedTeamTool
from alprina_cli.tools.security.blue_team import BlueTeamTool
from alprina_cli.tools.security.dfir import DFIRTool
from alprina_cli.tools.security.android_sast import AndroidSASTTool
from alprina_cli.tools.file.glob import GlobTool
from alprina_cli.tools.file.grep import GrepTool
from alprina_cli.tools.file.read import ReadFileTool

# Tool registry - tools are auto-registered here
ALL_TOOLS = [
    # Core security tools
    NetworkAnalyzerTool(),
    ScanTool(),
    ReconTool(),
    VulnScanTool(),
    ExploitTool(),
    # Specialized security tools
    RedTeamTool(),
    BlueTeamTool(),
    DFIRTool(),
    AndroidSASTTool(),
    # File tools (critical for context engineering)
    GlobTool(),
    GrepTool(),
    ReadFileTool(),
]


def register_tool(tool_instance):
    """Register a tool in the global registry"""
    ALL_TOOLS.append(tool_instance)
    return tool_instance


def get_tool_by_name(name: str):
    """
    Get tool by name from registry.

    Context: Just-in-time tool lookup (not pre-loading all tools).
    """
    for tool in ALL_TOOLS:
        if tool.name == name:
            return tool
    raise ValueError(f"Tool not found: {name}")


def get_all_tools():
    """Get all registered tools"""
    return ALL_TOOLS.copy()


__all__ = [
    # Base classes
    "AlprinaToolBase",
    "SyncToolBase",
    "ToolResult",
    "ToolOk",
    "ToolError",
    "TParams",
    # Registry functions
    "register_tool",
    "get_tool_by_name",
    "get_all_tools",
    "ALL_TOOLS"
]
