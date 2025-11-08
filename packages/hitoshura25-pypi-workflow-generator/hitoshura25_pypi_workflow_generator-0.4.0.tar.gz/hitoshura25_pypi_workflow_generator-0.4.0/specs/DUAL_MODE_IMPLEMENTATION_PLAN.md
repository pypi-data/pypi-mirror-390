# Dual-Mode Architecture Implementation Plan
## PyPI Workflow Generator: MCP Server + CLI Tool

**Goal**: Transform `pypi-workflow-generator` into a dual-mode tool that works as both an MCP-compliant server (for AI agents like Claude Code) and a traditional CLI tool (for non-MCP agents and developers).

**Reference Architecture**: `mcp-server-webauthn-client` (~/mpo-api-authn-server/mcp-server-webauthn-client)

---

## Executive Summary

This plan addresses:
1. **Critical packaging issues** preventing current deployment
2. **MCP server implementation** for AI agent integration
3. **Shared core logic** to avoid code duplication
4. **Backward compatibility** for existing CLI users
5. **Complete testing strategy** for both modes
6. **Documentation** for developers and AI agents

---

## Current State Assessment

### Critical Issues (BLOCKERS - Must Fix First)

#### 1. Missing `__init__.py` ⛔
**File**: `pypi_workflow_generator/__init__.py`
**Status**: Does not exist
**Impact**: Package builds as EMPTY (no Python modules included in wheel)
**Evidence**: Built wheel contains only metadata, no `.py` files

**Proof**:
```bash
# Current wheel contents (WRONG):
pypi_workflow_generator-0.0.post18.dist-info/licenses/LICENSE
pypi_workflow_generator-0.0.post18.dist-info/METADATA
pypi_workflow_generator-0.0.post18.dist-info/WHEEL
pypi_workflow_generator-0.0.post18.dist-info/entry_points.txt
pypi_workflow_generator-0.0.post18.dist-info/top_level.txt
pypi_workflow_generator-0.0.post18.dist-info/RECORD
# NO PYTHON FILES!
```

**Required**: Create `__init__.py` to mark directory as a package

#### 2. Missing Template Files in Distribution ⛔
**Files**: `*.j2` files (Jinja2 templates)
**Location**: `pypi_workflow_generator/*.j2`
**Impact**: Runtime errors when users try to generate workflows
**Root Cause**: No `MANIFEST.in` file to include non-Python files

**Templates Missing from Distribution**:
- `pypi_publish.yml.j2` - Main workflow template
- `setup.py.j2` - Setup.py template for init
- `pyproject.toml.j2` - Pyproject.toml template for init

**Required**: Create `MANIFEST.in` to include templates

#### 3. Placeholder Metadata ⛔
**File**: `setup.py:19-22`
**Status**: Contains dummy values
**Impact**: Cannot publish to PyPI with placeholder data

**Current Values (WRONG)**:
```python
author='Your Name',
author_email='your.email@example.com',
description='A tool to generate GitHub Actions workflows for Python packages.',
url='https://github.com/your-username/pypi-workflow-generator',
```

**Required**: Update with real metadata

#### 4. License Mismatch ⚠️
**Conflict**:
- `LICENSE` file: Apache License 2.0
- `setup.py` classifier: `"License :: OSI Approved :: MIT License"`

**Impact**: Legal confusion, PyPI validation warnings
**Required**: Update classifier to match Apache 2.0

### Medium Priority Issues

#### 5. Incomplete MCP Support
**Current**: Has `--mcp-input` JSON flag (MCP-friendly CLI)
**Missing**: True MCP server with stdio transport
**Gap**: Not discoverable by MCP-compliant agents

#### 6. No `tests/__init__.py`
**Location**: `pypi_workflow_generator/tests/`
**Impact**: Minor (pytest works without it)
**Note**: Good practice to add for consistency

#### 7. Documentation Gaps
**Missing**:
- Installation instructions for end users
- Quick start guide
- MCP integration examples
- AI agent discovery documentation
- Troubleshooting section

---

## Phase 1: Critical Fixes (Required Before Any MCP Work)

**Priority**: MUST DO FIRST
**Time Estimate**: 1-2 hours
**Blockers Removed**: Package will be installable and functional

### 1.1 Create `__init__.py`

**File**: `pypi_workflow_generator/__init__.py`

**Content**:
```python
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
from .main import generate_workflow
from .init import init_project
from .create_release import create_release_tag

__all__ = [
    'generate_workflow',
    'init_project',
    'create_release_tag',
]
```

**Why**: Makes `pypi_workflow_generator` a valid Python package that setuptools can find

### 1.2 Create `MANIFEST.in`

**File**: `MANIFEST.in` (project root)

**Content**:
```
# Include documentation
include README.md
include LICENSE
include requirements.txt

# Include templates (critical for runtime)
recursive-include pypi_workflow_generator *.j2

# Exclude development/planning docs from distribution
exclude PYPI_WORKFLOW_GENERATOR_PLAN.md
exclude SETUP_PY_GENERATION_PLAN.md
exclude DUAL_MODE_IMPLEMENTATION_PLAN.md

# Exclude git/IDE files
global-exclude .DS_Store
global-exclude __pycache__
global-exclude *.pyc
global-exclude *.pyo
```

**Why**: Ensures Jinja2 templates are included in source distribution and wheels

### 1.3 Update `setup.py` Metadata

**File**: `setup.py`

**Changes**:
```python
setup(
    name='pypi-workflow-generator',
    author='Vinayak Menon',  # Changed from 'Your Name'
    author_email='your.email@example.com',  # UPDATE WITH REAL EMAIL
    description='Dual-mode tool (MCP server + CLI) for generating GitHub Actions workflows for Python package publishing',
    url='https://github.com/hitoshura25/pypi-workflow-generator',  # UPDATE WITH REAL REPO
    use_scm_version={"local_scheme": local_scheme},
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,  # Uses MANIFEST.in
    install_requires=[
        'Jinja2>=3.0',
        # MCP dependencies will be added in Phase 2
    ],
    python_requires='>=3.8',  # Updated from 3.6 (EOL)
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",  # FIXED: was MIT
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Build Tools",
    ],
    entry_points={
        'console_scripts': [
            'pypi-workflow-generator=pypi_workflow_generator.main:main',
            'pypi-workflow-generator-init=pypi_workflow_generator.init:main',
            'pypi-release=pypi_workflow_generator.create_release:main',
        ],
    },
)
```

**Critical Changes**:
- ✅ Update author information
- ✅ Update repository URL
- ✅ Fix license classifier (MIT → Apache)
- ✅ Update Python version requirement (3.6 → 3.8+)
- ✅ Add more classifiers for better PyPI discoverability

### 1.4 Update `pyproject.toml`

**File**: `pyproject.toml`

**Add metadata section**:
```toml
[build-system]
requires = ["setuptools>=61.0", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "pypi-workflow-generator"
description = "Dual-mode tool (MCP server + CLI) for generating GitHub Actions workflows"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "Apache-2.0"}
authors = [
    {name = "Vinayak Menon", email = "your.email@example.com"}  # UPDATE EMAIL
]
keywords = ["mcp", "github-actions", "pypi", "workflow", "ci-cd", "code-generator"]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
]
dynamic = ["version"]

[project.urls]
Homepage = "https://github.com/hitoshura25/pypi-workflow-generator"  # UPDATE
Repository = "https://github.com/hitoshura25/pypi-workflow-generator"  # UPDATE
Issues = "https://github.com/hitoshura25/pypi-workflow-generator/issues"  # UPDATE

[tool.setuptools_scm]
version_scheme = "post-release"

[tool.setuptools.packages.find]
where = ["."]
include = ["pypi_workflow_generator*"]
exclude = ["tests*"]

[tool.setuptools.package-data]
pypi_workflow_generator = ["*.j2"]
```

**Why**: Modern Python packaging standard (PEP 621)

### 1.5 Verification Steps

**After Phase 1 completion, verify**:

```bash
# 1. Build package
python -m build --outdir /tmp/test-build

# 2. Inspect wheel contents
unzip -l /tmp/test-build/pypi_workflow_generator-*.whl

# Expected to see:
# - pypi_workflow_generator/__init__.py ✓
# - pypi_workflow_generator/main.py ✓
# - pypi_workflow_generator/init.py ✓
# - pypi_workflow_generator/create_release.py ✓
# - pypi_workflow_generator/pypi_publish.yml.j2 ✓
# - pypi_workflow_generator/setup.py.j2 ✓
# - pypi_workflow_generator/pyproject.toml.j2 ✓

# 3. Test installation
pip install /tmp/test-build/pypi_workflow_generator-*.whl

# 4. Verify commands work
pypi-workflow-generator --help
pypi-workflow-generator-init --help
pypi-release --help

# 5. Test actual workflow generation
mkdir /tmp/test-project && cd /tmp/test-project
echo "# Test" > README.md
pypi-workflow-generator-init --package-name test-pkg --author "Test" \
  --author-email "test@example.com" --description "Test" \
  --url "https://example.com" --command-name test-cmd
pypi-workflow-generator --python-version 3.11

# Verify files created:
ls -la .github/workflows/pypi-publish.yml
cat pyproject.toml
cat setup.py
```

**Success Criteria**:
- ✅ Wheel contains all Python files
- ✅ Wheel contains all `.j2` templates
- ✅ All console scripts are executable
- ✅ Workflow generation succeeds
- ✅ No errors during installation

---

## Phase 2: MCP Server Implementation

**Priority**: HIGH (enables AI agent integration)
**Time Estimate**: 3-4 hours
**Dependencies**: Phase 1 must be complete

### 2.1 Architecture Overview

**Dual Entry Point Pattern** (from mcp-server-webauthn-client):

```
pypi_workflow_generator/
├── __init__.py           # Package init (Phase 1)
├── server.py             # NEW: MCP server entry point
├── cli.py                # REFACTORED: CLI entry point (from main.py)
├── generator.py          # NEW: Shared core logic
├── init.py               # REFACTORED: Uses shared core
├── create_release.py     # REFACTORED: Uses shared core
├── pypi_publish.yml.j2   # Template (existing)
├── setup.py.j2           # Template (existing)
├── pyproject.toml.j2     # Template (existing)
└── tests/
    ├── __init__.py       # NEW
    ├── test_generator.py # UPDATED
    └── test_init.py      # UPDATED
```

**Flow**:
```
MCP Agents (Claude Code)     CLI Users/Non-MCP Agents
        │                             │
        ▼                             ▼
   server.py                      cli.py
        │                             │
        └──────────┬──────────────────┘
                   ▼
            generator.py
          (Shared Core Logic)
```

### 2.2 Add MCP Dependencies

**File**: `setup.py`

**Update `install_requires`**:
```python
install_requires=[
    'Jinja2>=3.0',
    'mcp>=1.0.0',  # MCP SDK for Python
],
```

**File**: `requirements.txt`

**Add**:
```
# Existing
pytest
Jinja2
pyyaml
twine
wheel
setuptools_scm
build

# New for MCP
mcp>=1.0.0
```

**Note**: Check if Python MCP SDK exists. If not available, we may need to use subprocess to call Node.js MCP server. Alternative: Create stdio-based server manually.

**Research Required**: Verify Python MCP SDK availability. If unavailable, consider:
- Option A: Implement stdio protocol manually (like webauthn example does in TypeScript)
- Option B: Create Node.js wrapper that calls Python CLI
- Option C: Use `@modelcontextprotocol/sdk` via subprocess

**Recommended**: Option A (manual stdio implementation) for pure Python solution.

### 2.3 Create Shared Core Module

**File**: `pypi_workflow_generator/generator.py`

**Purpose**: Extract core logic from `main.py` into reusable functions

**Content**:
```python
"""
Core workflow generation logic.

This module contains the shared business logic used by both:
- MCP server mode (server.py)
- CLI mode (cli.py)
"""

import os
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader


def generate_workflow(
    python_version: str = '3.11',
    output_filename: str = 'pypi-publish.yml',
    release_on_main_push: bool = False,
    test_path: str = '.',
    base_output_dir: Optional[str] = None,
    verbose_publish: bool = False
) -> Dict[str, Any]:
    """
    Generate GitHub Actions workflow for PyPI publishing.

    Args:
        python_version: Python version to use in workflow
        output_filename: Name of generated workflow file
        release_on_main_push: Trigger release on main branch push
        test_path: Path to tests directory
        base_output_dir: Custom output directory (default: .github/workflows)
        verbose_publish: Enable verbose mode for publish actions

    Returns:
        Dict with success status and generated file path

    Raises:
        FileNotFoundError: If pyproject.toml or setup.py missing
        ValueError: If parameters are invalid
    """
    # Validation
    if not os.path.exists('pyproject.toml') or not os.path.exists('setup.py'):
        raise FileNotFoundError(
            "Project not initialized. Run 'pypi-workflow-generator-init' first."
        )

    # Get template directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(script_dir))
    template = env.get_template('pypi_publish.yml.j2')

    # Render template
    workflow_content = template.render(
        python_version=python_version,
        release_on_main_push=release_on_main_push,
        verbose_publish=verbose_publish,
        test_path=test_path
    )

    # Construct output path
    output_dir = base_output_dir if base_output_dir else os.path.join(
        os.getcwd(), '.github', 'workflows'
    )
    os.makedirs(output_dir, exist_ok=True)
    full_output_path = os.path.join(output_dir, output_filename)

    # Write workflow file
    with open(full_output_path, 'w') as f:
        f.write(workflow_content)

    return {
        'success': True,
        'file_path': full_output_path,
        'message': f"Successfully generated {full_output_path}"
    }


def initialize_project(
    package_name: str,
    author: str,
    author_email: str,
    description: str,
    url: str,
    command_name: str
) -> Dict[str, Any]:
    """
    Initialize a new Python project with pyproject.toml and setup.py.

    Args:
        package_name: Name of the Python package
        author: Author name
        author_email: Author email
        description: Package description
        url: Project URL
        command_name: Command-line entry point name

    Returns:
        Dict with success status and created files
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(script_dir))

    # Render pyproject.toml
    pyproject_template = env.get_template('pyproject.toml.j2')
    pyproject_content = pyproject_template.render()

    # Render setup.py
    setup_template = env.get_template('setup.py.j2')
    setup_content = setup_template.render(
        package_name=package_name,
        author=author,
        author_email=author_email,
        description=description,
        url=url,
        command_name=command_name
    )

    # Write files
    with open('pyproject.toml', 'w') as f:
        f.write(pyproject_content)

    with open('setup.py', 'w') as f:
        f.write(setup_content)

    return {
        'success': True,
        'files_created': ['pyproject.toml', 'setup.py'],
        'message': 'Successfully initialized project with pyproject.toml and setup.py'
    }


def create_git_release(version: str) -> Dict[str, Any]:
    """
    Create and push a git release tag.

    Args:
        version: Version string (e.g., 'v1.0.0')

    Returns:
        Dict with success status

    Raises:
        subprocess.CalledProcessError: If git commands fail
    """
    import subprocess

    try:
        # Create tag
        subprocess.run(['git', 'tag', version], check=True)

        # Push tag
        subprocess.run(['git', 'push', 'origin', version], check=True)

        return {
            'success': True,
            'version': version,
            'message': f'Successfully created and pushed tag {version}'
        }
    except subprocess.CalledProcessError as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'Error creating or pushing tag: {e}'
        }
    except FileNotFoundError:
        return {
            'success': False,
            'error': 'git not found',
            'message': 'Git is not installed or not in PATH'
        }
```

### 2.4 Create MCP Server Entry Point

**File**: `pypi_workflow_generator/server.py`

**Content**:
```python
#!/usr/bin/env python3
"""
MCP Server for PyPI Workflow Generator.

This module implements the Model Context Protocol server that allows
AI agents to generate GitHub Actions workflows for Python package publishing.
"""

import sys
import json
import asyncio
from typing import Any, Dict, List

from .generator import generate_workflow, initialize_project, create_git_release


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
                    "name": "generate_workflow",
                    "description": "Generate GitHub Actions workflow for Python package publishing to PyPI with Trusted Publishers support",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "python_version": {
                                "type": "string",
                                "description": "Python version to use in workflow",
                                "default": "3.11"
                            },
                            "output_filename": {
                                "type": "string",
                                "description": "Name of generated workflow file",
                                "default": "pypi-publish.yml"
                            },
                            "release_on_main_push": {
                                "type": "boolean",
                                "description": "Trigger release on every main branch push",
                                "default": False
                            },
                            "test_path": {
                                "type": "string",
                                "description": "Path to tests directory",
                                "default": "."
                            },
                            "verbose_publish": {
                                "type": "boolean",
                                "description": "Enable verbose mode for publishing",
                                "default": False
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "initialize_project",
                    "description": "Initialize a new Python project with pyproject.toml and setup.py configured for PyPI publishing",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "package_name": {
                                "type": "string",
                                "description": "Name of the Python package"
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
            if tool_name == "generate_workflow":
                result = generate_workflow(**arguments)
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
                result = initialize_project(**arguments)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result['message']
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
```

### 2.5 Refactor CLI Entry Point

**File**: `pypi_workflow_generator/cli.py` (renamed from main.py)

**Content**:
```python
#!/usr/bin/env python3
"""
CLI entry point for PyPI Workflow Generator.

This module provides the command-line interface for generating
GitHub Actions workflows.
"""

import argparse
import json
from .generator import generate_workflow


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate a GitHub Actions workflow for Python package publishing.'
    )

    # CLI mode arguments
    parser.add_argument(
        '--python-version',
        default='3.11',
        help='The version of Python to use in the workflow (default: 3.11)'
    )
    parser.add_argument(
        '--output-filename',
        default='pypi-publish.yml',
        help='The name for the generated workflow file (default: pypi-publish.yml)'
    )
    parser.add_argument(
        '--release-on-main-push',
        action='store_true',
        help='Initiate the release on every main branch push'
    )
    parser.add_argument(
        '--test-path',
        default='.',
        help='The path to the tests (default: .)'
    )
    parser.add_argument(
        '--verbose-publish',
        action='store_true',
        help='Enable verbose mode for publishing actions'
    )

    # Legacy MCP mode argument (kept for backward compatibility)
    parser.add_argument(
        '--mcp-input',
        help='[DEPRECATED] Use MCP server mode instead. JSON string containing input parameters.'
    )

    args = parser.parse_args()

    if args.mcp_input:
        # Legacy MCP mode (deprecated but supported for backward compatibility)
        print("Warning: --mcp-input is deprecated. Use 'mcp-pypi-workflow-generator' for MCP server mode.")
        try:
            mcp_params = json.loads(args.mcp_input)
            python_version = mcp_params.get('python_version', '3.11')
            output_filename = mcp_params.get('output_filename', 'pypi-publish.yml')
            release_on_main_push = mcp_params.get('release_on_main_push', False)
            test_path = mcp_params.get('test_path', '.')
            verbose_publish = mcp_params.get('verbose_publish', False)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON string provided for --mcp-input: {e}")
            return 1
    else:
        # CLI mode
        python_version = args.python_version
        output_filename = args.output_filename
        release_on_main_push = args.release_on_main_push
        test_path = args.test_path
        verbose_publish = args.verbose_publish

    try:
        result = generate_workflow(
            python_version=python_version,
            output_filename=output_filename,
            release_on_main_push=release_on_main_push,
            test_path=test_path,
            verbose_publish=verbose_publish
        )
        print(result['message'])
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
```

### 2.6 Refactor `init.py`

**File**: `pypi_workflow_generator/init.py`

**Changes**: Use `initialize_project` from `generator.py`

```python
#!/usr/bin/env python3
"""
CLI for initializing new Python projects.
"""

import argparse
from .generator import initialize_project


def main():
    """Main entry point for project initialization."""
    parser = argparse.ArgumentParser(
        description='Initialize a new Python project with PyPI publishing workflow.'
    )
    parser.add_argument('--package-name', required=True, help='The name of the package')
    parser.add_argument('--author', required=True, help='The name of the author')
    parser.add_argument('--author-email', required=True, help='The email of the author')
    parser.add_argument('--description', required=True, help='A short description of the package')
    parser.add_argument('--url', required=True, help='The URL of the project')
    parser.add_argument('--command-name', required=True, help='The name of the command-line entry point')

    args = parser.parse_args()

    try:
        result = initialize_project(
            package_name=args.package_name,
            author=args.author,
            author_email=args.author_email,
            description=args.description,
            url=args.url,
            command_name=args.command_name
        )
        print(result['message'])
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
```

### 2.7 Refactor `create_release.py`

**File**: `pypi_workflow_generator/create_release.py`

**Changes**: Use `create_git_release` from `generator.py`

```python
#!/usr/bin/env python3
"""
CLI for creating git release tags.
"""

import argparse
from .generator import create_git_release


def main():
    """Main entry point for creating releases."""
    parser = argparse.ArgumentParser(description='Create and push a git version tag.')
    parser.add_argument('version', help='The version string for the tag (e.g., v1.0.0)')

    args = parser.parse_args()

    result = create_git_release(args.version)
    print(result['message'])
    return 0 if result['success'] else 1


if __name__ == "__main__":
    exit(main())
```

### 2.8 Update Entry Points in `setup.py`

**File**: `setup.py`

**Update `entry_points` section**:
```python
entry_points={
    'console_scripts': [
        # CLI mode (existing, now points to cli.py)
        'pypi-workflow-generator=pypi_workflow_generator.cli:main',
        'pypi-workflow-generator-init=pypi_workflow_generator.init:main',
        'pypi-release=pypi_workflow_generator.create_release:main',

        # MCP mode (new)
        'mcp-pypi-workflow-generator=pypi_workflow_generator.server:main',
    ],
},
```

### 2.9 Add MCP Metadata to `package.json` Equivalent

**Note**: Python packages don't use `package.json`, but we can add MCP metadata to setup.py or create a discovery file.

**Option 1**: Create `.mcp-config.json` in project root

**File**: `.mcp-config.json`

```json
{
  "name": "pypi-workflow-generator",
  "version": "1.0.0",
  "protocol": "stdio",
  "server": "mcp-pypi-workflow-generator",
  "capabilities": ["tools"],
  "tools": {
    "generate_workflow": {
      "description": "Generate GitHub Actions workflow for PyPI publishing",
      "frameworks": ["Python"]
    },
    "initialize_project": {
      "description": "Initialize new Python project with PyPI configuration"
    },
    "create_release": {
      "description": "Create git release tag"
    }
  },
  "documentation": "https://github.com/hitoshura25/pypi-workflow-generator/blob/main/README.md",
  "repository": "https://github.com/hitoshura25/pypi-workflow-generator"
}
```

**Option 2**: Add metadata to `setup.py` under `project_urls`

```python
project_urls={
    'Homepage': 'https://github.com/hitoshura25/pypi-workflow-generator',
    'Repository': 'https://github.com/hitoshura25/pypi-workflow-generator',
    'Issues': 'https://github.com/hitoshura25/pypi-workflow-generator/issues',
    'MCP Documentation': 'https://github.com/hitoshura25/pypi-workflow-generator/blob/main/MCP-USAGE.md',
}
```

---

## Phase 3: Testing Strategy

**Priority**: HIGH
**Time Estimate**: 2-3 hours
**Dependencies**: Phase 2 complete

### 3.1 Create `tests/__init__.py`

**File**: `pypi_workflow_generator/tests/__init__.py`

```python
"""
Test suite for PyPI Workflow Generator.
"""
```

### 3.2 Update Existing Tests

**File**: `pypi_workflow_generator/tests/test_generator.py`

**Updates**: Import from `generator` module instead of `main`

```python
from pypi_workflow_generator.generator import generate_workflow


def test_generate_workflow_default_arguments(tmp_path):
    """Test workflow generation with default arguments."""
    output_dir = tmp_path / ".github" / "workflows"

    # Create dummy project files
    (tmp_path / "pyproject.toml").write_text("[build-system]\n")
    (tmp_path / "setup.py").write_text("from setuptools import setup\nsetup()")

    result = generate_workflow(
        python_version='3.11',
        output_filename='pypi-publish.yml',
        release_on_main_push=False,
        test_path='.',
        base_output_dir=str(output_dir),
        verbose_publish=False
    )

    assert result['success'] == True
    output_file = output_dir / 'pypi-publish.yml'
    assert output_file.exists()
    # ... rest of assertions


def test_generate_workflow_custom_arguments(tmp_path):
    """Test workflow generation with custom arguments."""
    # Similar updates...
```

**File**: `pypi_workflow_generator/tests/test_init.py`

**Updates**: Import from `generator` module

```python
import os
from pypi_workflow_generator.generator import initialize_project


def test_init_project(tmp_path):
    """Test project initialization."""
    os.chdir(tmp_path)

    result = initialize_project(
        package_name='my-package',
        author='My Name',
        author_email='my.email@example.com',
        description='My new package.',
        url='https://github.com/my-username/my-package',
        command_name='my-command'
    )

    assert result['success'] == True
    assert os.path.exists('pyproject.toml')
    assert os.path.exists('setup.py')
    # ... rest of assertions
```

### 3.3 Add MCP Server Tests

**File**: `pypi_workflow_generator/tests/test_server.py`

```python
"""
Tests for MCP server functionality.
"""

import json
import asyncio
import pytest
from pypi_workflow_generator.server import MCPServer


@pytest.mark.asyncio
async def test_list_tools():
    """Test that list_tools returns correct tool definitions."""
    server = MCPServer()
    result = await server.handle_list_tools()

    assert "tools" in result
    assert len(result["tools"]) == 3

    tool_names = [tool["name"] for tool in result["tools"]]
    assert "generate_workflow" in tool_names
    assert "initialize_project" in tool_names
    assert "create_release" in tool_names


@pytest.mark.asyncio
async def test_call_tool_generate_workflow(tmp_path):
    """Test calling generate_workflow tool via MCP."""
    server = MCPServer()

    # Create dummy project files
    import os
    os.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[build-system]\n")
    (tmp_path / "setup.py").write_text("from setuptools import setup\nsetup()")

    result = await server.handle_call_tool(
        "generate_workflow",
        {
            "python_version": "3.11",
            "output_filename": "test-workflow.yml",
            "base_output_dir": str(tmp_path)
        }
    )

    assert "content" in result
    assert len(result["content"]) > 0
    assert result["content"][0]["type"] == "text"
    assert "Successfully generated" in result["content"][0]["text"]
    assert result.get("isError") == False


@pytest.mark.asyncio
async def test_call_tool_unknown():
    """Test calling unknown tool returns error."""
    server = MCPServer()

    result = await server.handle_call_tool("unknown_tool", {})

    assert result.get("isError") == True
    assert "Unknown tool" in result["content"][0]["text"]


@pytest.mark.asyncio
async def test_handle_request_list_tools():
    """Test handling list_tools request."""
    server = MCPServer()

    request = {
        "id": 1,
        "method": "tools/list",
        "params": {}
    }

    response = await server.handle_request(request)

    assert "tools" in response
    assert len(response["tools"]) > 0


@pytest.mark.asyncio
async def test_handle_request_call_tool(tmp_path):
    """Test handling call_tool request."""
    server = MCPServer()

    import os
    os.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[build-system]\n")
    (tmp_path / "setup.py").write_text("from setuptools import setup\nsetup()")

    request = {
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "generate_workflow",
            "arguments": {
                "python_version": "3.11",
                "base_output_dir": str(tmp_path)
            }
        }
    }

    response = await server.handle_request(request)

    assert "content" in response
    assert response.get("isError") == False


@pytest.mark.asyncio
async def test_handle_request_unknown_method():
    """Test handling unknown method returns error."""
    server = MCPServer()

    request = {
        "id": 3,
        "method": "unknown/method",
        "params": {}
    }

    response = await server.handle_request(request)

    assert "error" in response
    assert response["error"]["code"] == -32601
```

### 3.4 Add Integration Tests

**File**: `pypi_workflow_generator/tests/test_integration.py`

```python
"""
Integration tests for dual-mode functionality.
"""

import os
import subprocess
import tempfile
import pytest


def test_cli_help():
    """Test that CLI help works."""
    result = subprocess.run(
        ['python', '-m', 'pypi_workflow_generator.cli', '--help'],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert 'usage:' in result.stdout.lower()


def test_cli_generates_workflow(tmp_path):
    """Test that CLI can generate workflow."""
    os.chdir(tmp_path)

    # Create dummy project files
    (tmp_path / "pyproject.toml").write_text("[build-system]\n")
    (tmp_path / "setup.py").write_text("from setuptools import setup\nsetup()")

    result = subprocess.run(
        ['python', '-m', 'pypi_workflow_generator.cli', '--python-version', '3.11'],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert (tmp_path / ".github" / "workflows" / "pypi-publish.yml").exists()


def test_init_cli_creates_files(tmp_path):
    """Test that init CLI creates project files."""
    os.chdir(tmp_path)

    result = subprocess.run([
        'python', '-m', 'pypi_workflow_generator.init',
        '--package-name', 'test-pkg',
        '--author', 'Test Author',
        '--author-email', 'test@example.com',
        '--description', 'Test package',
        '--url', 'https://example.com',
        '--command-name', 'test-cmd'
    ], capture_output=True, text=True)

    assert result.returncode == 0
    assert (tmp_path / "pyproject.toml").exists()
    assert (tmp_path / "setup.py").exists()


@pytest.mark.asyncio
async def test_mcp_server_stdio():
    """Test MCP server via stdio (basic smoke test)."""
    # This is a basic test - real MCP clients would use more complex interaction
    import asyncio

    # Start server process
    proc = await asyncio.create_subprocess_exec(
        'python', '-m', 'pypi_workflow_generator.server',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # Send list_tools request
    request = {"id": 1, "method": "tools/list", "params": {}}
    request_json = json.dumps(request) + "\n"

    proc.stdin.write(request_json.encode())
    await proc.stdin.drain()

    # Read response (with timeout)
    try:
        line = await asyncio.wait_for(proc.stdout.readline(), timeout=5.0)
        response = json.loads(line.decode())

        assert "tools" in response
        assert len(response["tools"]) > 0
    finally:
        proc.kill()
        await proc.wait()
```

### 3.5 Test Execution

```bash
# Run all tests
pytest pypi_workflow_generator/tests/ -v

# Run with coverage
pytest pypi_workflow_generator/tests/ --cov=pypi_workflow_generator --cov-report=html

# Run specific test files
pytest pypi_workflow_generator/tests/test_server.py -v
pytest pypi_workflow_generator/tests/test_integration.py -v
```

---

## Phase 4: Documentation Updates

**Priority**: MEDIUM
**Time Estimate**: 2 hours
**Dependencies**: Phases 1-3 complete

### 4.1 Update Main README

**File**: `README.md`

**Add sections**:

```markdown
# pypi-workflow-generator

A dual-mode tool (MCP server + CLI) for generating GitHub Actions workflows for Python package publishing to PyPI.

## Features

- ✅ **Dual-Mode Operation**: Works as MCP server for AI agents OR traditional CLI for developers
- ✅ **PyPI Trusted Publishers**: Secure publishing without API tokens
- ✅ **Automated Versioning**: Uses setuptools_scm for git-based versioning
- ✅ **Pre-release Testing**: Automatic TestPyPI publishing on pull requests
- ✅ **Production Publishing**: Automatic PyPI publishing on version tags
- ✅ **Complete Project Initialization**: Generates pyproject.toml and setup.py
- ✅ **Release Management**: Simple git tag creation for triggering releases

## Installation

```bash
pip install pypi-workflow-generator
```

## Usage

This package can be used in three ways:

### 1. MCP Mode (For AI Agents)

For AI agents with MCP support (Claude Code, Continue.dev, Cline):

**Add to `claude_config.json`**:
```json
{
  "mcpServers": {
    "pypi-workflow-generator": {
      "command": "mcp-pypi-workflow-generator"
    }
  }
}
```

The agent can now use these tools:
- `generate_workflow` - Generate GitHub Actions workflow
- `initialize_project` - Create pyproject.toml and setup.py
- `create_release` - Create and push git release tags

**Example conversation**:
```
You: "Please set up a PyPI publishing workflow for my Python project"

Claude: I'll help you set up a complete PyPI publishing workflow.

[Calls initialize_project and generate_workflow tools]

✅ Created:
  - pyproject.toml
  - setup.py
  - .github/workflows/pypi-publish.yml

Next steps:
1. Configure Trusted Publishers on PyPI
2. Create a release: pypi-release v1.0.0
```

### 2. CLI Mode (For Developers)

**Initialize a new project**:
```bash
pypi-workflow-generator-init \
  --package-name my-awesome-package \
  --author "Your Name" \
  --author-email "your.email@example.com" \
  --description "My awesome Python package" \
  --url "https://github.com/username/my-awesome-package" \
  --command-name my-command
```

**Generate workflow**:
```bash
pypi-workflow-generator --python-version 3.11
```

**Create a release**:
```bash
pypi-release v1.0.0
```

### 3. Programmatic Use

```python
from pypi_workflow_generator import generate_workflow, initialize_project

# Initialize project
initialize_project(
    package_name="my-package",
    author="Your Name",
    author_email="your@email.com",
    description="My package",
    url="https://github.com/user/repo",
    command_name="my-cmd"
)

# Generate workflow
generate_workflow(
    python_version="3.11",
    release_on_main_push=False
)
```

## Generated Workflow Features

The generated `pypi-publish.yml` workflow includes:

- **Automated Testing**: Runs pytest on every PR and release
- **Pre-release Publishing**: TestPyPI publishing on PRs with version like `1.0.0.dev123`
- **Production Publishing**: PyPI publishing on version tags
- **Trusted Publishers**: No API tokens needed (OIDC authentication)
- **setuptools_scm**: Automatic versioning from git tags

## Setting Up Trusted Publishers

Before your workflow can publish to PyPI:

1. **Create your package on PyPI** (first time only)
2. **Navigate to publishing settings**:
   - TestPyPI: `https://test.pypi.org/manage/project/<package-name>/settings/publishing/`
   - PyPI: `https://pypi.org/manage/project/<package-name>/settings/publishing/`

3. **Add GitHub Actions publisher**:
   - Owner: `your-github-username`
   - Repository: `your-repo-name`
   - Workflow: `pypi-publish.yml`
   - Environment: (leave blank)

4. **Done!** No API tokens needed.

## CLI Options

### `pypi-workflow-generator`

Generate GitHub Actions workflow for PyPI publishing.

```
Options:
  --python-version VERSION    Python version (default: 3.11)
  --output-filename NAME      Workflow filename (default: pypi-publish.yml)
  --release-on-main-push      Trigger release on main branch push
  --test-path PATH            Path to tests (default: .)
  --verbose-publish           Enable verbose publishing
```

### `pypi-workflow-generator-init`

Initialize a new Python project with PyPI configuration.

```
Options:
  --package-name NAME         Package name (required)
  --author NAME               Author name (required)
  --author-email EMAIL        Author email (required)
  --description TEXT          Package description (required)
  --url URL                   Project URL (required)
  --command-name NAME         CLI command name (required)
```

### `pypi-release`

Create and push a git release tag.

```
Usage:
  pypi-release v1.0.0
```

## MCP Server Details

The MCP server runs via stdio transport and provides three tools:

**Tool: `generate_workflow`**
- Generates GitHub Actions workflow file
- Parameters: python_version, output_filename, release_on_main_push, test_path, verbose_publish

**Tool: `initialize_project`**
- Creates pyproject.toml and setup.py
- Parameters: package_name, author, author_email, description, url, command_name

**Tool: `create_release`**
- Creates and pushes git tag
- Parameters: version

## Architecture

```
User/AI Agent
      │
      ├─── MCP Mode ────────> server.py (MCP protocol)
      │                           │
      ├─── CLI Mode ────────> cli.py (argparse)
      │                           │
      └─── Programmatic ────> __init__.py
                                  │
                    All modes use shared core:
                                  ▼
                            generator.py
                      (Business logic)
```

## Development

```bash
# Clone repository
git clone https://github.com/hitoshura25/pypi-workflow-generator.git
cd pypi-workflow-generator

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Build package
python -m build
```

## Contributing

Contributions welcome! Please open an issue or PR.

## License

Apache-2.0

## Links

- **Repository**: https://github.com/hitoshura25/pypi-workflow-generator
- **Issues**: https://github.com/hitoshura25/pypi-workflow-generator/issues
- **PyPI**: https://pypi.org/project/pypi-workflow-generator/
```

### 4.2 Create MCP Usage Guide

**File**: `MCP-USAGE.md`

```markdown
# MCP Usage Guide

Complete guide for using pypi-workflow-generator as an MCP server.

## What is MCP?

Model Context Protocol (MCP) is a standard protocol that allows AI agents to interact with external tools. This package implements an MCP server that AI agents can use to generate PyPI publishing workflows.

## Supported AI Agents

- ✅ Claude Code (Anthropic)
- ✅ Continue.dev
- ✅ Cline
- ⚠️ Cursor, Aider, Windsurf (use CLI mode instead)

## Configuration

### Claude Code

Add to your project's `claude_config.json`:

```json
{
  "mcpServers": {
    "pypi-workflow-generator": {
      "command": "mcp-pypi-workflow-generator"
    }
  }
}
```

### Continue.dev

Add to `~/.continue/config.json`:

```json
{
  "mcpServers": [
    {
      "name": "pypi-workflow-generator",
      "command": "mcp-pypi-workflow-generator"
    }
  ]
}
```

## Available Tools

### 1. generate_workflow

Generate GitHub Actions workflow for PyPI publishing.

**Parameters**:
- `python_version` (string, optional): Python version, default "3.11"
- `output_filename` (string, optional): Workflow filename, default "pypi-publish.yml"
- `release_on_main_push` (boolean, optional): Trigger on main push, default false
- `test_path` (string, optional): Tests directory, default "."
- `verbose_publish` (boolean, optional): Verbose publishing, default false

**Example**:
```json
{
  "python_version": "3.11",
  "output_filename": "pypi-publish.yml",
  "release_on_main_push": false,
  "test_path": "tests",
  "verbose_publish": true
}
```

### 2. initialize_project

Initialize new Python project with PyPI configuration.

**Parameters** (all required):
- `package_name` (string): Package name
- `author` (string): Author name
- `author_email` (string): Author email
- `description` (string): Package description
- `url` (string): Project URL
- `command_name` (string): CLI command name

**Example**:
```json
{
  "package_name": "my-package",
  "author": "Jane Doe",
  "author_email": "jane@example.com",
  "description": "My awesome package",
  "url": "https://github.com/janedoe/my-package",
  "command_name": "my-cli"
}
```

### 3. create_release

Create and push git release tag.

**Parameters**:
- `version` (string, required): Version tag (e.g., "v1.0.0")

**Example**:
```json
{
  "version": "v1.0.0"
}
```

## Example Workflows

### Complete Project Setup

```
You: "Set up my Python project for PyPI publishing"

Agent: I'll set up your Python project with a complete PyPI publishing workflow.

[Agent calls initialize_project]
Created pyproject.toml and setup.py

[Agent calls generate_workflow]
Generated .github/workflows/pypi-publish.yml

Your project is now configured for PyPI publishing with:
- Automated versioning via setuptools_scm
- TestPyPI publishing on pull requests
- PyPI publishing on version tags
- Trusted Publishers (no API tokens needed)

Next steps:
1. Configure Trusted Publishers on PyPI
2. Create your first release with: pypi-release v1.0.0
```

### Just Generate Workflow

```
You: "Generate a PyPI workflow using Python 3.12"

Agent: [Calls generate_workflow with python_version="3.12"]

Generated .github/workflows/pypi-publish.yml with Python 3.12
```

### Create Release

```
You: "Create a v2.0.0 release"

Agent: [Calls create_release with version="v2.0.0"]

Created and pushed tag v2.0.0
GitHub Actions will now build and publish to PyPI
```

## Troubleshooting

### Agent Can't Find MCP Server

**Issue**: Agent reports "mcp-pypi-workflow-generator not found"

**Solution**:
```bash
# Verify installation
pip list | grep pypi-workflow-generator

# Verify command exists
which mcp-pypi-workflow-generator

# Reinstall if needed
pip install --force-reinstall pypi-workflow-generator
```

### Tool Execution Fails

**Issue**: Tool returns error

**Check**:
1. For `generate_workflow`: Project must have `pyproject.toml` and `setup.py`
2. For `create_release`: Git repository must be initialized
3. For `initialize_project`: All required parameters must be provided

### Non-MCP Agents

**Issue**: Your AI agent doesn't support MCP

**Solution**: Use CLI mode instead:
```bash
pypi-workflow-generator-init --package-name my-pkg --author "Name" ...
pypi-workflow-generator --python-version 3.11
pypi-release v1.0.0
```

## Protocol Details

The MCP server uses:
- **Transport**: stdio (JSON-RPC over stdin/stdout)
- **Protocol Version**: MCP 1.0
- **Capabilities**: tools
- **Request Format**: JSON-RPC 2.0

## Development

Testing the MCP server:

```bash
# Start server
mcp-pypi-workflow-generator

# Send request (in another terminal)
echo '{"id":1,"method":"tools/list","params":{}}' | mcp-pypi-workflow-generator

# Expected response:
{"id": 1, "tools": [...]}
```
```

### 4.3 Update Package README

**File**: `pypi_workflow_generator/README.md`

**Update with dual-mode information**:

```markdown
# `pypi_workflow_generator` Package

Core logic for generating GitHub Actions workflows for Python packages.

## Architecture

This package implements a dual-mode architecture:

```
Entry Points:
├── server.py      → MCP server (for AI agents)
├── cli.py         → CLI interface (for developers)
├── init.py        → Project initialization
└── create_release.py → Release management

Shared Core:
└── generator.py   → Business logic (used by all modes)
```

## Modules

### `generator.py`

Core business logic with reusable functions:

- `generate_workflow()` - Generate GitHub Actions workflow
- `initialize_project()` - Create pyproject.toml and setup.py
- `create_git_release()` - Create and push git tags

### `server.py`

MCP server implementation:

- Implements stdio-based MCP protocol
- Provides tools for AI agents
- Wraps generator functions with MCP response format

### `cli.py`

Command-line interface:

- Argument parsing with argparse
- User-friendly error messages
- Wraps generator functions for CLI use

### `init.py`

Project initialization CLI:

- Creates pyproject.toml and setup.py
- Interactive or argument-based configuration

### `create_release.py`

Release management CLI:

- Creates git tags
- Pushes tags to remote

## Templates

### `pypi_publish.yml.j2`

Jinja2 template for GitHub Actions workflow:

Variables:
- `python_version` - Python version
- `release_on_main_push` - Trigger mode
- `test_path` - Test directory
- `verbose_publish` - Verbose mode

### `setup.py.j2`

Jinja2 template for setup.py:

Variables:
- `package_name`
- `author`
- `author_email`
- `description`
- `url`
- `command_name`

### `pyproject.toml.j2`

Jinja2 template for pyproject.toml:

Variables: (none - static template)

## Usage Examples

### As Library

```python
from pypi_workflow_generator import generate_workflow

result = generate_workflow(
    python_version="3.11",
    release_on_main_push=False
)
print(result['message'])
```

### MCP Mode

```bash
mcp-pypi-workflow-generator  # Starts stdio server
```

### CLI Mode

```bash
pypi-workflow-generator --python-version 3.11
```
```

---

## Phase 5: Final Verification & Deployment

**Priority**: HIGH
**Time Estimate**: 2 hours
**Dependencies**: All previous phases

### 5.1 Pre-Deployment Checklist

**Complete this checklist before publishing**:

- [ ] All critical issues from Phase 1 fixed
- [ ] Package builds successfully with all files included
- [ ] All tests pass (pytest)
- [ ] Both CLI and MCP modes work
- [ ] Documentation is complete and accurate
- [ ] LICENSE file is correct (Apache 2.0)
- [ ] Metadata in setup.py is correct (no placeholders)
- [ ] README examples work
- [ ] .gitignore includes build artifacts

### 5.2 Build Verification

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build package
python -m build

# Verify wheel contents
unzip -l dist/pypi_workflow_generator-*.whl

# MUST include:
# - pypi_workflow_generator/__init__.py
# - pypi_workflow_generator/server.py
# - pypi_workflow_generator/cli.py (or main.py)
# - pypi_workflow_generator/generator.py
# - pypi_workflow_generator/init.py
# - pypi_workflow_generator/create_release.py
# - pypi_workflow_generator/*.j2 (all templates)
# - pypi_workflow_generator/tests/*.py

# Verify source distribution
tar -tzf dist/pypi_workflow_generator-*.tar.gz | grep -E "\\.py$|\\.j2$"
```

### 5.3 Local Installation Test

```bash
# Create fresh virtual environment
python -m venv /tmp/test-venv
source /tmp/test-venv/bin/activate

# Install from wheel
pip install dist/pypi_workflow_generator-*.whl

# Test all entry points
pypi-workflow-generator --help
pypi-workflow-generator-init --help
pypi-release --help
mcp-pypi-workflow-generator --help  # Should show usage or start server

# Test actual functionality
mkdir /tmp/test-project && cd /tmp/test-project
echo "# Test Project" > README.md

# Initialize project
pypi-workflow-generator-init \
  --package-name test-pkg \
  --author "Test Author" \
  --author-email "test@example.com" \
  --description "Test package" \
  --url "https://github.com/test/test-pkg" \
  --command-name test-cmd

# Generate workflow
pypi-workflow-generator --python-version 3.11

# Verify files
ls -la pyproject.toml setup.py .github/workflows/pypi-publish.yml

# Test MCP server (basic check)
echo '{"id":1,"method":"tools/list","params":{}}' | mcp-pypi-workflow-generator
# Should return JSON with tools list

# Cleanup
deactivate
rm -rf /tmp/test-venv /tmp/test-project
```

### 5.4 TestPyPI Deployment

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ pypi-workflow-generator

# Verify it works
pypi-workflow-generator --help
```

### 5.5 Production PyPI Deployment

**Only after TestPyPI verification**:

```bash
# Upload to production PyPI
twine upload dist/*

# Verify package page
# https://pypi.org/project/pypi-workflow-generator/

# Test installation
pip install pypi-workflow-generator
```

### 5.6 Post-Deployment Verification

```bash
# Fresh installation test
python -m venv /tmp/verify-venv
source /tmp/verify-venv/bin/activate

pip install pypi-workflow-generator

# Test all modes
pypi-workflow-generator --help
mcp-pypi-workflow-generator  # Ctrl+C to stop

# Cleanup
deactivate
rm -rf /tmp/verify-venv
```

---

## File Modification Summary

### Files to CREATE:

1. `pypi_workflow_generator/__init__.py` ⭐ CRITICAL
2. `MANIFEST.in` ⭐ CRITICAL
3. `pypi_workflow_generator/server.py` (MCP server)
4. `pypi_workflow_generator/generator.py` (shared core)
5. `pypi_workflow_generator/cli.py` (refactored from main.py)
6. `pypi_workflow_generator/tests/__init__.py`
7. `pypi_workflow_generator/tests/test_server.py`
8. `pypi_workflow_generator/tests/test_integration.py`
9. `MCP-USAGE.md`
10. `.mcp-config.json` (optional)

### Files to MODIFY:

1. `setup.py` ⭐ CRITICAL (metadata, entry points, dependencies)
2. `pyproject.toml` ⭐ CRITICAL (add project metadata)
3. `README.md` (add dual-mode documentation)
4. `pypi_workflow_generator/init.py` (use generator.py)
5. `pypi_workflow_generator/create_release.py` (use generator.py)
6. `pypi_workflow_generator/README.md` (update architecture docs)
7. `pypi_workflow_generator/tests/test_generator.py` (update imports)
8. `pypi_workflow_generator/tests/test_init.py` (update imports)
9. `.gitignore` (add build artifacts if missing)

### Files to DELETE/RENAME:

1. `pypi_workflow_generator/main.py` → RENAME to `cli.py` (or keep and modify)
2. `PYPI_WORKFLOW_GENERATOR_PLAN.md` → Keep but exclude from distribution
3. `SETUP_PY_GENERATION_PLAN.md` → Keep but exclude from distribution

---

## Risk Assessment

### High Risk Areas:

1. **Template inclusion** - If MANIFEST.in is wrong, templates won't be in distribution
2. **Entry points** - If setup.py entry_points are wrong, commands won't work
3. **Import paths** - Refactoring may break imports if not done carefully
4. **MCP protocol** - Stdio communication must be implemented correctly

### Mitigation Strategies:

1. Test package build after each phase
2. Verify entry points work before proceeding
3. Run tests frequently during refactoring
4. Test MCP server with actual MCP client (Claude Code)

---

## Success Criteria

✅ Package installs from PyPI without errors
✅ All four console scripts work: `pypi-workflow-generator`, `pypi-workflow-generator-init`, `pypi-release`, `mcp-pypi-workflow-generator`
✅ CLI mode generates working workflows
✅ MCP server responds to `tools/list` and `tools/call` requests
✅ Claude Code can discover and use the MCP server
✅ All tests pass
✅ Documentation is complete and accurate
✅ No placeholder values in metadata

---

## Timeline Estimate

| Phase | Time | Dependencies |
|-------|------|--------------|
| Phase 1: Critical Fixes | 1-2 hours | None |
| Phase 2: MCP Implementation | 3-4 hours | Phase 1 |
| Phase 3: Testing | 2-3 hours | Phase 2 |
| Phase 4: Documentation | 2 hours | Phase 3 |
| Phase 5: Deployment | 2 hours | Phase 4 |
| **Total** | **10-13 hours** | Sequential |

---

## Next Steps

1. Review this plan
2. Create a new branch: `git checkout -b feat/dual-mode-architecture`
3. Start with Phase 1 (Critical Fixes)
4. Test after each phase
5. Commit frequently with descriptive messages
6. Open PR when ready for review

---

## References

- **Reference Implementation**: `~/mpo-api-authn-server/mcp-server-webauthn-client`
- **MCP Specification**: https://modelcontextprotocol.io/
- **Python Packaging**: https://packaging.python.org/
- **setuptools_scm**: https://github.com/pypa/setuptools_scm

---

**Document Version**: 1.0
**Created**: 2025-10-31
**Status**: Ready for Implementation
