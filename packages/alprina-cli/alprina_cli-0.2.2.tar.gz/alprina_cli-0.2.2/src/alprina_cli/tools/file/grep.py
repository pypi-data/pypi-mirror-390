"""
Grep Tool - Content Search

Context Engineering:
- Search file contents for patterns
- Limits results to prevent context bloat
- Returns relevant context around matches
- Supports regex patterns

Based on: Kimi-CLI Grep tool (simplified, no ripgrep dependency)
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field
from loguru import logger

from alprina_cli.tools.base import AlprinaToolBase, ToolOk, ToolError


MAX_MATCHES = 100  # Context-efficient limit


class GrepParams(BaseModel):
    """
    Parameters for grep content search.

    Context: Focused schema for pattern searching.
    """
    pattern: str = Field(
        description="Regular expression pattern to search for"
    )
    path: str = Field(
        default=".",
        description="File or directory to search in"
    )
    file_pattern: str = Field(
        default="*",
        description="Glob pattern to filter files (e.g., '*.py', '*.{js,ts}')"
    )
    ignore_case: bool = Field(
        default=False,
        description="Case-insensitive search"
    )
    context_lines: int = Field(
        default=0,
        description="Number of lines to show before/after match (0 = match only)"
    )
    max_matches: int = Field(
        default=MAX_MATCHES,
        description=f"Maximum matches to return (default: {MAX_MATCHES})"
    )
    output_mode: Literal["content", "files_only", "count"] = Field(
        default="files_only",
        description="Output mode: content (show matches), files_only (just paths), count (count matches)"
    )


class GrepTool(AlprinaToolBase[GrepParams]):
    """
    Search file contents for patterns.

    Context Engineering Benefits:
    - Just-in-time content discovery
    - Configurable max_matches to control context
    - Context lines for relevant code
    - Multiple output modes for different needs

    Output Modes:
    - files_only: Just file paths (minimal context)
    - content: Matching lines with context
    - count: Number of matches (most compact)

    Usage:
    ```python
    tool = GrepTool()
    result = await tool.execute(GrepParams(
        pattern="def.*scan",
        path="./src",
        file_pattern="*.py",
        output_mode="files_only"
    ))
    ```
    """

    name: str = "Grep"
    description: str = """Search file contents for regex patterns.

Capabilities:
- Regex pattern matching
- File filtering by glob pattern
- Case-sensitive/insensitive search
- Context lines around matches
- Multiple output modes

Returns: Matches based on output_mode (files_only, content, or count)"""
    params: type[GrepParams] = GrepParams

    async def execute(self, params: GrepParams) -> ToolOk | ToolError:
        """
        Execute grep search.

        Context: Returns limited results based on output_mode.
        """
        logger.debug(f"Grep: '{params.pattern}' in {params.path}")

        try:
            # Compile regex pattern
            flags = re.IGNORECASE if params.ignore_case else 0
            try:
                regex = re.compile(params.pattern, flags)
            except re.error as e:
                return ToolError(
                    message=f"Invalid regex pattern: {str(e)}",
                    brief="Invalid pattern"
                )

            # Resolve path
            search_path = Path(params.path).expanduser()
            if not search_path.is_absolute():
                search_path = Path.cwd() / search_path

            if not search_path.exists():
                return ToolError(
                    message=f"Path not found: {params.path}",
                    brief="Path not found"
                )

            # Perform search
            if search_path.is_file():
                results = self._search_file(search_path, regex, params)
            else:
                results = self._search_directory(search_path, regex, params)

            # Format output based on mode
            return self._format_results(results, params)

        except Exception as e:
            logger.error(f"Grep search failed: {e}")
            return ToolError(
                message=f"Grep search failed: {str(e)}",
                brief="Grep failed"
            )

    def _search_file(
        self,
        file_path: Path,
        regex: re.Pattern,
        params: GrepParams
    ) -> List[Dict[str, Any]]:
        """Search a single file"""
        try:
            content = file_path.read_text(errors="ignore")
            lines = content.splitlines()

            matches = []
            for line_num, line in enumerate(lines, 1):
                if regex.search(line):
                    match_data = {
                        "file": str(file_path),
                        "line_number": line_num,
                        "line": line,
                        "context_before": [],
                        "context_after": []
                    }

                    # Add context lines if requested
                    if params.context_lines > 0:
                        start = max(0, line_num - params.context_lines - 1)
                        end = min(len(lines), line_num + params.context_lines)

                        match_data["context_before"] = lines[start:line_num-1]
                        match_data["context_after"] = lines[line_num:end]

                    matches.append(match_data)

            return matches

        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return []

    def _search_directory(
        self,
        dir_path: Path,
        regex: re.Pattern,
        params: GrepParams
    ) -> List[Dict[str, Any]]:
        """Search all files in directory matching file_pattern"""
        all_matches = []

        # Find matching files
        try:
            files = dir_path.rglob(params.file_pattern)
        except Exception:
            files = dir_path.glob(params.file_pattern)

        for file_path in files:
            if file_path.is_file():
                file_matches = self._search_file(file_path, regex, params)
                all_matches.extend(file_matches)

                # Stop if we hit max_matches
                if len(all_matches) >= params.max_matches:
                    break

        return all_matches[:params.max_matches]

    def _format_results(
        self,
        results: List[Dict[str, Any]],
        params: GrepParams
    ) -> ToolOk:
        """Format results based on output_mode"""

        if not results:
            return ToolOk(
                content={"matches": []},
                output="No matches found",
                metadata={"message": "No matches found"}
            )

        if params.output_mode == "count":
            # Just count matches
            count = len(results)
            return ToolOk(
                content={"count": count},
                output=f"{count} matches found",
                metadata={"message": f"Found {count} matches"}
            )

        elif params.output_mode == "files_only":
            # Just unique file paths
            files = list(set(r["file"] for r in results))
            files.sort()

            return ToolOk(
                content={"files": files, "total_matches": len(results)},
                output="\n".join(files),
                metadata={"message": f"Found matches in {len(files)} files"}
            )

        else:  # content mode
            # Show full matches with context
            output_lines = []

            for match in results:
                output_lines.append(f"\n{match['file']}:{match['line_number']}")
                output_lines.append("-" * 40)

                # Context before
                for line in match["context_before"]:
                    output_lines.append(f"  {line}")

                # The matching line
                output_lines.append(f"> {match['line']}")

                # Context after
                for line in match["context_after"]:
                    output_lines.append(f"  {line}")

            return ToolOk(
                content={
                    "matches": results,
                    "total": len(results)
                },
                output="\n".join(output_lines),
                metadata={"message": f"Found {len(results)} matches"}
            )
