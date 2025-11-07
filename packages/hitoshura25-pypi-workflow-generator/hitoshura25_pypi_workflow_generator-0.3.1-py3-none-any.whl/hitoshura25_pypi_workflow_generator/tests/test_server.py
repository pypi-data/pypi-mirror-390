"""
Tests for MCP server functionality.
"""

import os
import pytest
from hitoshura25_pypi_workflow_generator.server import MCPServer

@pytest.mark.asyncio
async def test_list_tools():
    """Test that list_tools returns correct tool definitions."""
    server = MCPServer()
    result = await server.handle_list_tools()

    assert "tools" in result
    assert len(result["tools"]) == 3

    tool_names = [tool["name"] for tool in result["tools"]]
    assert "generate_workflows" in tool_names
    assert "initialize_project" in tool_names
    assert "create_release" in tool_names

    # Verify each tool has required fields
    for tool in result["tools"]:
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool
        assert "type" in tool["inputSchema"]
        assert "properties" in tool["inputSchema"]


@pytest.mark.asyncio
async def test_list_tools_schema_validation():
    """Test that tool schemas are properly defined."""
    server = MCPServer()
    result = await server.handle_list_tools()

    # Check generate_workflows schema
    gen_tool = next(t for t in result["tools"] if t["name"] == "generate_workflows")
    assert "python_version" in gen_tool["inputSchema"]["properties"]
    assert "test_path" in gen_tool["inputSchema"]["properties"]
    assert "verbose_publish" in gen_tool["inputSchema"]["properties"]
    assert gen_tool["inputSchema"]["required"] == []

    # Check initialize_project schema
    init_tool = next(t for t in result["tools"] if t["name"] == "initialize_project")
    assert "package_name" in init_tool["inputSchema"]["properties"]
    assert "author" in init_tool["inputSchema"]["properties"]
    assert "author_email" in init_tool["inputSchema"]["properties"]
    assert set(init_tool["inputSchema"]["required"]) == {
        "package_name", "author", "author_email", "description", "url", "command_name"
    }

    # Check create_release schema
    release_tool = next(t for t in result["tools"] if t["name"] == "create_release")
    assert "version" in release_tool["inputSchema"]["properties"]
    assert release_tool["inputSchema"]["required"] == ["version"]


@pytest.mark.asyncio
async def test_call_tool_generate_workflows(tmp_path):
    """Test calling generate_workflows tool via MCP."""
    server = MCPServer()

    # Change to temp directory
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        # Create dummy project files (required for workflow generation)
        (tmp_path / "pyproject.toml").write_text("[build-system]\n")
        (tmp_path / "setup.py").write_text("from setuptools import setup\nsetup()")

        result = await server.handle_call_tool(
            "generate_workflows",
            {
                "python_version": "3.11"
            }
        )

        assert "content" in result
        assert len(result["content"]) > 0
        assert result["content"][0]["type"] == "text"
        assert "Successfully generated" in result["content"][0]["text"]
        assert result.get("isError") == False

        # Verify all 3 workflow files were created
        reusable_path = tmp_path / ".github" / "workflows" / "_reusable-test-build.yml"
        release_path = tmp_path / ".github" / "workflows" / "release.yml"
        test_pr_path = tmp_path / ".github" / "workflows" / "test-pr.yml"

        assert reusable_path.exists()
        assert release_path.exists()
        assert test_pr_path.exists()

        # Verify script file was created and is executable
        script_path = tmp_path / "scripts" / "calculate_version.sh"
        assert script_path.exists()
        assert script_path.is_file()
        assert script_path.stat().st_mode & 0o111  # Check executable bit

        # Verify content has correct Python version
        content = reusable_path.read_text()
        assert "3.11" in content

    finally:
        os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_call_tool_generate_workflows_with_options(tmp_path):
    """Test calling generate_workflows with custom options."""
    server = MCPServer()

    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        # Create dummy project files (required for workflow generation)
        (tmp_path / "pyproject.toml").write_text("[build-system]\n")
        (tmp_path / "setup.py").write_text("from setuptools import setup\nsetup()")

        result = await server.handle_call_tool(
            "generate_workflows",
            {
                "python_version": "3.10",
                "test_path": "tests/",
                "verbose_publish": True
            }
        )

        assert result.get("isError") == False
        assert "Successfully generated" in result["content"][0]["text"]

        # Verify all 3 files were created
        reusable_path = tmp_path / ".github" / "workflows" / "_reusable-test-build.yml"
        release_path = tmp_path / ".github" / "workflows" / "release.yml"
        test_pr_path = tmp_path / ".github" / "workflows" / "test-pr.yml"

        assert reusable_path.exists()
        assert release_path.exists()
        assert test_pr_path.exists()

        # Verify custom options
        content = reusable_path.read_text()
        assert "3.10" in content
        # Verify test_path is actually used in pytest command
        assert "pytest" in content
        assert "${{ inputs.test_path }}" in content or "pytest tests/" in content

    finally:
        os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_call_tool_initialize_project(tmp_path):
    """Test calling initialize_project tool via MCP."""
    server = MCPServer()

    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        result = await server.handle_call_tool(
            "initialize_project",
            {
                "package_name": "test-package",
                "author": "Test Author",
                "author_email": "test@example.com",
                "description": "A test package",
                "url": "https://github.com/test/test-package",
                "command_name": "test-cmd",
                "prefix": "NONE"  # Skip prefix for this test
            }
        )

        assert "content" in result
        assert result.get("isError") == False
        # New message format
        assert "Created package:" in result["content"][0]["text"]
        assert "test_package" in result["content"][0]["text"]  # import name
        assert "test-package" in result["content"][0]["text"]  # package name

        # Verify files were created
        assert (tmp_path / "pyproject.toml").exists()
        assert (tmp_path / "setup.py").exists()
        assert (tmp_path / "test_package").exists()  # package directory

        # Verify content
        setup_content = (tmp_path / "setup.py").read_text()
        assert "test-package" in setup_content
        assert "Test Author" in setup_content
        assert "test@example.com" in setup_content
        assert "test-cmd" in setup_content

    finally:
        os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_call_tool_initialize_project_missing_args():
    """Test that initialize_project fails with missing required arguments."""
    server = MCPServer()

    result = await server.handle_call_tool(
        "initialize_project",
        {
            "package_name": "test-package"
            # Missing other required fields
        }
    )

    # Should return an error
    assert result.get("isError") == True
    assert "content" in result


@pytest.mark.asyncio
async def test_call_tool_create_release():
    """Test calling create_release tool via MCP."""
    server = MCPServer()

    # Note: This will fail in a non-git repo, but we can test the call structure
    result = await server.handle_call_tool(
        "create_release",
        {
            "version": "v1.0.0"
        }
    )

    # Should have content (either success or error message)
    assert "content" in result
    assert "isError" in result


@pytest.mark.asyncio
async def test_call_tool_unknown():
    """Test calling unknown tool returns error."""
    server = MCPServer()

    result = await server.handle_call_tool("unknown_tool", {})

    assert result.get("isError") == True
    assert "Unknown tool" in result["content"][0]["text"]


@pytest.mark.asyncio
async def test_handle_request_list_tools():
    """Test handling a full JSON-RPC request for tools/list."""
    server = MCPServer()

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }

    response = await server.handle_request(request)

    assert "tools" in response
    assert len(response["tools"]) == 3


@pytest.mark.asyncio
async def test_handle_request_call_tool():
    """Test handling a full JSON-RPC request for tools/call."""
    server = MCPServer()

    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "generate_workflows",
            "arguments": {
                "python_version": "3.11"
            }
        }
    }

    response = await server.handle_request(request)

    assert "content" in response


@pytest.mark.asyncio
async def test_handle_request_unknown_method():
    """Test handling unknown method returns error."""
    server = MCPServer()

    request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "unknown/method",
        "params": {}
    }

    response = await server.handle_request(request)

    assert "error" in response
    assert response["error"]["code"] == -32601
    assert "Method not found" in response["error"]["message"]


def test_mcp_server_imports():
    """Test that MCP server can be imported successfully."""
    from hitoshura25_pypi_workflow_generator.server import MCPServer, main

    assert MCPServer is not None
    assert main is not None
    assert callable(main)


@pytest.mark.asyncio
async def test_generate_workflows_creates_all_files_via_mcp(tmp_path):
    """Test that generate_workflows MCP tool creates all 3 workflow files."""
    server = MCPServer()

    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        # Create dummy project files
        (tmp_path / "pyproject.toml").write_text("[build-system]\n")
        (tmp_path / "setup.py").write_text("from setuptools import setup\nsetup()")

        result = await server.handle_call_tool(
            "generate_workflows",
            {"python_version": "3.11"}
        )

        assert result.get("isError") == False

        # All 3 workflows should exist
        assert (tmp_path / ".github" / "workflows" / "_reusable-test-build.yml").exists()
        assert (tmp_path / ".github" / "workflows" / "release.yml").exists()
        assert (tmp_path / ".github" / "workflows" / "test-pr.yml").exists()

    finally:
        os.chdir(original_cwd)
