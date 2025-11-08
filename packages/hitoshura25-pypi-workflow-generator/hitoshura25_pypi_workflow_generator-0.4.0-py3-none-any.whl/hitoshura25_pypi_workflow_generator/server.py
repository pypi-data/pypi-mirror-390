#!/usr/bin/env python3
"""
MCP Server for PyPI Workflow Generator.

This module implements the Model Context Protocol server that allows
AI agents to generate GitHub Actions workflows for Python package publishing.
"""

import sys
import json
import asyncio
from typing import Any, Dict

from .generator import generate_workflows, initialize_project, create_git_release


class MCPServer:
    """
    Model Context Protocol server implementation.

    Implements stdio-based communication protocol for AI agents.
    """

    def __init__(self):
        self.name = "pypi-workflow-generator"
        self.version = "1.0.0"

    async def handle_list_tools(self) -> Dict[str, Any]:
        """List available tools for AI agents."""
        return {
            "tools": [
                {
                    "name": "generate_workflows",
                    "description": "Generate GitHub Actions workflows for Python package publishing to PyPI. Creates 3 files: _reusable-test-build.yml (shared test/build logic), release.yml (manual releases), and test-pr.yml (PR testing). No PAT required - uses default GITHUB_TOKEN.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "python_version": {
                                "type": "string",
                                "description": "Python version to use in workflows",
                                "default": "3.11"
                            },
                            "test_path": {
                                "type": "string",
                                "description": "Path to tests directory",
                                "default": "."
                            },
                            "verbose_publish": {
                                "type": "boolean",
                                "description": "Enable verbose mode for PyPI publishing",
                                "default": False
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "initialize_project",
                    "description": "Initialize a new Python project with pyproject.toml and setup.py configured for PyPI publishing. By default, auto-detects git username as prefix to avoid PyPI naming conflicts.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "package_name": {
                                "type": "string",
                                "description": "Base package name (without prefix)"
                            },
                            "author": {
                                "type": "string",
                                "description": "Author name"
                            },
                            "author_email": {
                                "type": "string",
                                "description": "Author email address"
                            },
                            "description": {
                                "type": "string",
                                "description": "Short package description"
                            },
                            "url": {
                                "type": "string",
                                "description": "Project homepage URL"
                            },
                            "command_name": {
                                "type": "string",
                                "description": "Command-line entry point name"
                            },
                            "prefix": {
                                "type": "string",
                                "description": "Package name prefix. Use 'AUTO' to auto-detect from git (default), explicit string for custom prefix, or 'NONE' to skip prefix.",
                                "default": "AUTO"
                            }
                        },
                        "required": ["package_name", "author", "author_email", "description", "url", "command_name"]
                    }
                },
                {
                    "name": "create_release",
                    "description": "Create and push a git release tag to trigger PyPI publishing workflow",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "version": {
                                "type": "string",
                                "description": "Version tag (e.g., 'v1.0.0')"
                            }
                        },
                        "required": ["version"]
                    }
                }
            ]
        }

    async def handle_call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given arguments."""
        try:
            if tool_name == "generate_workflows":
                result = generate_workflows(**arguments)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result['message']
                        }
                    ],
                    "isError": not result['success']
                }

            elif tool_name == "initialize_project":
                # Handle prefix parameter - convert "NONE" string to None
                if 'prefix' in arguments:
                    if arguments['prefix'] == 'NONE':
                        arguments['prefix'] = None
                    elif arguments['prefix'] == '':
                        # Default to AUTO if not specified
                        arguments['prefix'] = 'AUTO'
                else:
                    # Default to AUTO
                    arguments['prefix'] = 'AUTO'

                result = initialize_project(**arguments)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result.get('message', result.get('error', 'Unknown error'))
                        }
                    ],
                    "isError": not result['success']
                }

            elif tool_name == "create_release":
                result = create_git_release(arguments['version'])
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result['message']
                        }
                    ],
                    "isError": not result['success']
                }

            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Unknown tool: {tool_name}"
                        }
                    ],
                    "isError": True
                }

        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing {tool_name}: {str(e)}"
                    }
                ],
                "isError": True
            }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request."""
        method = request.get("method")
        params = request.get("params", {})

        if method == "tools/list":
            return await self.handle_list_tools()

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            return await self.handle_call_tool(tool_name, arguments)

        else:
            return {
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    async def run(self):
        """Run the MCP server using stdio transport."""
        print(f"PyPI Workflow Generator MCP server running on stdio", file=sys.stderr)

        while True:
            try:
                # Read JSON-RPC request from stdin
                line = sys.stdin.readline()
                if not line:
                    break

                request = json.loads(line)

                # Handle request
                response = await self.handle_request(request)

                # Add request ID to response
                if "id" in request:
                    response["id"] = request["id"]

                # Write JSON-RPC response to stdout
                print(json.dumps(response), flush=True)

            except json.JSONDecodeError as e:
                error_response = {
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)

            except Exception as e:
                error_response = {
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)


def main():
    """Main entry point for MCP server."""
    server = MCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
