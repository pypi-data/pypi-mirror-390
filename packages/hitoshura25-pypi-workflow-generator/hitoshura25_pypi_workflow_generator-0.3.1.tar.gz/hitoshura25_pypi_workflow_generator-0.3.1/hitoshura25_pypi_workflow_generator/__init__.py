"""
PyPI Workflow Generator

A dual-mode tool for generating GitHub Actions workflows for Python package publishing.

- MCP Mode: For AI agents (Claude Code, Continue.dev, Cline)
- CLI Mode: For developers and non-MCP agents (Cursor, Aider, Windsurf)
"""

__version__ = "0.1.0"  # Will be overridden by setuptools_scm
__author__ = "Vinayak Menon"
__license__ = "Apache-2.0"

# Export main functions for programmatic use
from .generator import (
    generate_workflows,
    initialize_project,
    create_git_release,
)

__all__ = [
    '__version__',
    '__author__',
    '__license__',
    'generate_workflows',
    'initialize_project',
    'create_git_release',
]
