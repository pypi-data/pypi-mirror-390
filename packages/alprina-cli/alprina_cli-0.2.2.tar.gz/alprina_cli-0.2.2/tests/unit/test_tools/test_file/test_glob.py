"""
Tests for GlobTool

Context: Validates file pattern matching for just-in-time discovery.
"""

import pytest
import tempfile
from pathlib import Path
from alprina_cli.tools.file.glob import GlobTool, GlobParams
from alprina_cli.tools.base import ToolOk, ToolError


@pytest.mark.asyncio
async def test_glob_tool_creation():
    """Test creating glob tool"""
    tool = GlobTool()
    assert tool.name == "Glob"
    assert tool.params == GlobParams


@pytest.mark.asyncio
async def test_glob_simple_pattern():
    """Test simple glob pattern"""
    tool = GlobTool()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        (Path(temp_dir) / "file1.py").touch()
        (Path(temp_dir) / "file2.py").touch()
        (Path(temp_dir) / "file3.txt").touch()

        params = GlobParams(pattern="*.py", directory=temp_dir)
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)
        assert len(result.content["matches"]) == 2
        assert all(".py" in m for m in result.content["matches"])


@pytest.mark.asyncio
async def test_glob_recursive_pattern():
    """Test recursive glob pattern"""
    tool = GlobTool()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create nested structure
        (Path(temp_dir) / "src").mkdir()
        (Path(temp_dir) / "src" / "file1.py").touch()
        (Path(temp_dir) / "tests").mkdir()
        (Path(temp_dir) / "tests" / "test1.py").touch()

        params = GlobParams(pattern="*/*.py", directory=temp_dir)
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)
        assert len(result.content["matches"]) == 2


@pytest.mark.asyncio
async def test_glob_no_matches():
    """Test pattern with no matches"""
    tool = GlobTool()

    with tempfile.TemporaryDirectory() as temp_dir:
        params = GlobParams(pattern="*.nonexistent", directory=temp_dir)
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)
        assert len(result.content["matches"]) == 0
        assert result.content["total_found"] == 0


@pytest.mark.asyncio
async def test_glob_max_results_limit():
    """Test max_results parameter"""
    tool = GlobTool()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create many files
        for i in range(20):
            (Path(temp_dir) / f"file{i}.txt").touch()

        params = GlobParams(pattern="*.txt", directory=temp_dir, max_results=10)
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)
        assert len(result.content["matches"]) == 10
        assert result.content["total_found"] == 20
        assert result.content["truncated"] is True


@pytest.mark.asyncio
async def test_glob_include_dirs():
    """Test including directories in results"""
    tool = GlobTool()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create files and dirs
        (Path(temp_dir) / "file.txt").touch()
        (Path(temp_dir) / "subdir").mkdir()

        # Without include_dirs
        params = GlobParams(pattern="*.txt", directory=temp_dir, include_dirs=False)
        result = await tool.execute(params)
        assert isinstance(result, ToolOk)
        assert len(result.content["matches"]) == 1

        # With include_dirs - use a pattern that matches both
        params = GlobParams(pattern="*", directory=temp_dir, include_dirs=True, max_results=500)
        result = await tool.execute(params)
        # Pattern "*" is too broad, should return error
        assert isinstance(result, ToolError)


@pytest.mark.asyncio
async def test_glob_unsafe_pattern():
    """Test validation of unsafe patterns"""
    tool = GlobTool()

    # Pattern starting with **
    params = GlobParams(pattern="**/*.py", directory=".")
    result = await tool.execute(params)
    assert isinstance(result, ToolError)
    assert "not allowed" in result.message

    # Pattern too broad
    params = GlobParams(pattern="*", directory=".")
    result = await tool.execute(params)
    assert isinstance(result, ToolError)


@pytest.mark.asyncio
async def test_glob_nonexistent_directory():
    """Test with nonexistent directory"""
    tool = GlobTool()

    params = GlobParams(pattern="*.py", directory="/nonexistent/path")
    result = await tool.execute(params)

    assert isinstance(result, ToolError)
    assert "not found" in result.message.lower()


@pytest.mark.asyncio
async def test_glob_invalid_directory():
    """Test with file instead of directory"""
    tool = GlobTool()

    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_file = f.name

    try:
        params = GlobParams(pattern="*.py", directory=temp_file)
        result = await tool.execute(params)

        assert isinstance(result, ToolError)
        assert "not a directory" in result.message.lower()
    finally:
        Path(temp_file).unlink()


@pytest.mark.asyncio
async def test_glob_relative_paths():
    """Test that results are relative paths"""
    tool = GlobTool()

    with tempfile.TemporaryDirectory() as temp_dir:
        (Path(temp_dir) / "test.py").touch()

        params = GlobParams(pattern="*.py", directory=temp_dir)
        result = await tool.execute(params)

        assert isinstance(result, ToolOk)
        # Should be relative path, not absolute
        assert not result.content["matches"][0].startswith("/")


def test_glob_to_dict():
    """Test tool serialization"""
    tool = GlobTool()
    tool_dict = tool.to_dict()

    assert tool_dict["name"] == "Glob"
    assert "pattern" in tool_dict["parameters"]["properties"]
