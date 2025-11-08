"""
Glob Tool - File Pattern Matching

Context Engineering:
- Enables just-in-time file discovery
- Limits results to prevent context bloat
- Safe pattern validation
- Returns relative paths (more readable)

Based on: Kimi-CLI Glob tool (simplified for Alprina)
"""

from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
from loguru import logger

from alprina_cli.tools.base import AlprinaToolBase, ToolOk, ToolError


MAX_MATCHES = 500  # Context-efficient limit


class GlobParams(BaseModel):
    """
    Parameters for glob file search.

    Context: Simple, focused schema for file discovery.
    """
    pattern: str = Field(
        description="Glob pattern to match files (e.g., '*.py', 'src/**/*.js')"
    )
    directory: str = Field(
        default=".",
        description="Directory to search in (default: current directory)"
    )
    include_dirs: bool = Field(
        default=False,
        description="Include directories in results (default: files only)"
    )
    max_results: int = Field(
        default=MAX_MATCHES,
        description=f"Maximum results to return (default: {MAX_MATCHES})"
    )


class GlobTool(AlprinaToolBase[GlobParams]):
    """
    File pattern matching tool using glob syntax.

    Context Engineering Benefits:
    - Just-in-time file discovery (not pre-loading entire codebase)
    - Configurable max_results to prevent context bloat
    - Returns relative paths (more readable, less tokens)
    - Safe pattern validation (prevents ** at root)

    Glob Patterns:
    - `*.py` - All Python files in directory
    - `**/*.py` - All Python files recursively
    - `src/**/*.{js,ts}` - JS/TS files in src/
    - `test_*.py` - Files starting with test_

    Usage:
    ```python
    tool = GlobTool()
    result = await tool.execute(GlobParams(
        pattern="**/*.py",
        directory="./src"
    ))
    # Returns: List of matching file paths
    ```
    """

    name: str = "Glob"
    description: str = """Find files matching glob patterns.

Capabilities:
- Glob pattern matching (*, **, ?, [])
- Recursive directory search
- File/directory filtering
- Result limiting (context control)

Returns: List of matching file paths (relative to search directory)"""
    params: type[GlobParams] = GlobParams

    async def execute(self, params: GlobParams) -> ToolOk | ToolError:
        """
        Execute glob file search.

        Context: Returns limited, relative paths for efficiency.
        """
        logger.debug(f"Glob: {params.pattern} in {params.directory}")

        try:
            # Validate pattern
            error = self._validate_pattern(params.pattern)
            if error:
                return error

            # Resolve directory
            dir_path = Path(params.directory).expanduser()
            if not dir_path.is_absolute():
                dir_path = Path.cwd() / dir_path

            # Validate directory
            if not dir_path.exists():
                return ToolError(
                    message=f"Directory not found: {params.directory}",
                    brief="Directory not found"
                )

            if not dir_path.is_dir():
                return ToolError(
                    message=f"Not a directory: {params.directory}",
                    brief="Invalid directory"
                )

            # Perform glob search
            matches = self._glob_search(dir_path, params.pattern, params.include_dirs)

            # Limit results for context efficiency
            total_found = len(matches)
            if len(matches) > params.max_results:
                matches = matches[:params.max_results]
                truncated = True
            else:
                truncated = False

            # Convert to relative paths (more readable)
            relative_paths = []
            for match in matches:
                try:
                    rel_path = match.relative_to(dir_path)
                    relative_paths.append(str(rel_path))
                except ValueError:
                    # If can't make relative, use absolute
                    relative_paths.append(str(match))

            # Build result message
            if total_found == 0:
                message = f"No matches found for pattern '{params.pattern}'"
            elif truncated:
                message = (
                    f"Found {total_found} matches for '{params.pattern}'. "
                    f"Showing first {params.max_results}. "
                    "Use a more specific pattern or increase max_results."
                )
            else:
                message = f"Found {total_found} matches for '{params.pattern}'"

            return ToolOk(
                content={
                    "matches": relative_paths,
                    "total_found": total_found,
                    "truncated": truncated,
                    "directory": str(dir_path),
                    "pattern": params.pattern
                },
                output="\n".join(relative_paths) if relative_paths else "(no matches)",
                metadata={"message": message}
            )

        except Exception as e:
            logger.error(f"Glob search failed: {e}")
            return ToolError(
                message=f"Glob search failed: {str(e)}",
                brief="Glob failed"
            )

    def _validate_pattern(self, pattern: str) -> ToolError | None:
        """
        Validate glob pattern safety.

        Context: Prevent patterns that would search too broadly.
        """
        # Prevent starting with ** (would search everything)
        if pattern.startswith("**"):
            return ToolError(
                message=(
                    f"Pattern '{pattern}' starts with '**' which is not allowed. "
                    "This would recursively search all directories and may be too broad. "
                    "Use a more specific pattern like 'src/**/*.py' instead."
                ),
                brief="Unsafe pattern"
            )

        # Warn about very broad patterns
        if pattern == "*" or pattern == "**/*":
            return ToolError(
                message=(
                    f"Pattern '{pattern}' is too broad and would match everything. "
                    "Use a more specific pattern with file extensions or directory names."
                ),
                brief="Pattern too broad"
            )

        return None

    def _glob_search(
        self,
        directory: Path,
        pattern: str,
        include_dirs: bool
    ) -> List[Path]:
        """
        Perform glob search.

        Context: Returns sorted list for consistent output.
        """
        matches = list(directory.glob(pattern))

        # Filter out directories if not requested
        if not include_dirs:
            matches = [p for p in matches if p.is_file()]

        # Sort for consistent output (helps with context)
        matches.sort()

        return matches
