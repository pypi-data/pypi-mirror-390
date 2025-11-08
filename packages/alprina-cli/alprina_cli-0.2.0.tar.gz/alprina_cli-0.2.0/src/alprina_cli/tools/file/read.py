"""
Read File Tool

Context Engineering:
- Just-in-time file reading
- Supports partial file reading (line ranges)
- Token-efficient output
- Binary file detection

Simple, focused tool for reading files on-demand.
"""

from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from loguru import logger

from alprina_cli.tools.base import AlprinaToolBase, ToolOk, ToolError


MAX_LINES = 1000  # Context-efficient limit


class ReadFileParams(BaseModel):
    """
    Parameters for file reading.

    Context: Simple schema for reading files.
    """
    file_path: str = Field(
        description="Path to file to read"
    )
    start_line: Optional[int] = Field(
        default=None,
        description="Start reading from this line (1-indexed, inclusive)"
    )
    end_line: Optional[int] = Field(
        default=None,
        description="Stop reading at this line (1-indexed, inclusive)"
    )
    max_lines: int = Field(
        default=MAX_LINES,
        description=f"Maximum lines to read (default: {MAX_LINES})"
    )


class ReadFileTool(AlprinaToolBase[ReadFileParams]):
    """
    Read file contents.

    Context Engineering Benefits:
    - Just-in-time file reading (not pre-loading)
    - Partial file reading (line ranges)
    - Max lines limit for context control
    - Binary file detection

    Usage:
    ```python
    tool = ReadFileTool()

    # Read entire file
    result = await tool.execute(ReadFileParams(
        file_path="./src/main.py"
    ))

    # Read specific lines
    result = await tool.execute(ReadFileParams(
        file_path="./src/main.py",
        start_line=10,
        end_line=50
    ))
    ```
    """

    name: str = "ReadFile"
    description: str = """Read file contents.

Capabilities:
- Read entire files or line ranges
- Binary file detection
- Context-efficient (max line limits)
- Line numbering

Returns: File contents with line numbers"""
    params: type[ReadFileParams] = ReadFileParams

    async def execute(self, params: ReadFileParams) -> ToolOk | ToolError:
        """
        Execute file read.

        Context: Returns limited, line-numbered content.
        """
        logger.debug(f"ReadFile: {params.file_path}")

        try:
            # Resolve file path
            file_path = Path(params.file_path).expanduser()
            if not file_path.is_absolute():
                file_path = Path.cwd() / file_path

            # Check file exists
            if not file_path.exists():
                return ToolError(
                    message=f"File not found: {params.file_path}",
                    brief="File not found"
                )

            if not file_path.is_file():
                return ToolError(
                    message=f"Not a file: {params.file_path}",
                    brief="Not a file"
                )

            # Check if binary file
            if self._is_binary(file_path):
                return ToolError(
                    message=f"File appears to be binary: {params.file_path}",
                    brief="Binary file"
                )

            # Read file
            try:
                content = file_path.read_text(errors="ignore")
            except Exception as e:
                return ToolError(
                    message=f"Could not read file: {str(e)}",
                    brief="Read failed"
                )

            lines = content.splitlines()
            total_lines = len(lines)

            # Determine line range
            start = (params.start_line or 1) - 1  # Convert to 0-indexed
            end = (params.end_line or total_lines) if params.end_line else total_lines

            # Validate range
            if start < 0:
                start = 0
            if end > total_lines:
                end = total_lines
            if start >= end:
                return ToolError(
                    message=f"Invalid line range: {start+1}-{end}",
                    brief="Invalid range"
                )

            # Extract lines
            selected_lines = lines[start:end]

            # Apply max_lines limit
            if len(selected_lines) > params.max_lines:
                selected_lines = selected_lines[:params.max_lines]
                truncated = True
            else:
                truncated = False

            # Format with line numbers
            numbered_lines = []
            for i, line in enumerate(selected_lines, start=start+1):
                numbered_lines.append(f"{i:4d} | {line}")

            output = "\n".join(numbered_lines)

            # Build message
            if truncated:
                message = (
                    f"Read lines {start+1}-{start+params.max_lines} of {total_lines} "
                    f"(truncated to {params.max_lines} lines)"
                )
            elif params.start_line or params.end_line:
                message = f"Read lines {start+1}-{end} of {total_lines}"
            else:
                message = f"Read {len(selected_lines)} lines"

            return ToolOk(
                content={
                    "file_path": str(file_path),
                    "total_lines": total_lines,
                    "start_line": start + 1,
                    "end_line": start + len(selected_lines),
                    "lines_returned": len(selected_lines),
                    "truncated": truncated
                },
                output=output,
                metadata={"message": message}
            )

        except Exception as e:
            logger.error(f"Read file failed: {e}")
            return ToolError(
                message=f"Read file failed: {str(e)}",
                brief="Read failed"
            )

    def _is_binary(self, file_path: Path) -> bool:
        """
        Check if file is binary.

        Context: Quick heuristic to avoid reading binary files.
        """
        try:
            # Read first 8192 bytes
            with open(file_path, 'rb') as f:
                chunk = f.read(8192)

            # Check for null bytes (common in binary files)
            if b'\x00' in chunk:
                return True

            # Try to decode as text
            try:
                chunk.decode('utf-8')
                return False
            except UnicodeDecodeError:
                return True

        except Exception:
            return False
