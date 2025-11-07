# MCP Server Generator Implementation Plan
## A Meta-Generator for Creating Dual-Mode MCP Servers

**Project**: `mcp-server-generator`
**Purpose**: Generate complete, production-ready MCP servers with dual-mode architecture (MCP protocol + CLI)
**Status**: Ready to implement (pypi-workflow-generator COMPLETED ✅)
**Created**: 2025-10-31
**Updated**: 2025-11-01

---

## Executive Summary

Build a template-based generator that creates complete MCP server projects with:
- ✅ **Dual-mode architecture** (MCP stdio server + CLI interface)
- ✅ **GitHub Actions workflows** (via pypi-workflow-generator integration)
- ✅ **Complete project structure** (tests, docs, packaging)
- ✅ **Best practices** (type hints, error handling, documentation)
- ✅ **Multi-language support** (Python initially, TypeScript/Go later)

**Key Innovation**: This tool itself will be an MCP server, so AI agents can use it to generate other MCP servers!

---

## Table of Contents

1. [Project Goals](#project-goals)
2. [Reference Architecture](#reference-architecture)
3. [What Gets Generated](#what-gets-generated)
4. [Architecture Overview](#architecture-overview)
5. [Implementation Phases](#implementation-phases)
6. [Template Structure](#template-structure)
7. [Tool Schema](#tool-schema)
8. [Testing Strategy](#testing-strategy)
9. [Documentation Plan](#documentation-plan)
10. [Deployment Strategy](#deployment-strategy)
11. [Future Enhancements](#future-enhancements)

---

## Project Goals

### Primary Goals

1. **Accelerate MCP Server Development**
   - Reduce setup time from hours to minutes
   - Eliminate boilerplate code duplication
   - Enforce best practices automatically

2. **Standardize MCP Server Architecture**
   - Consistent dual-mode pattern across all servers
   - Shared testing patterns
   - Common documentation structure

3. **Integrate with Existing Tools**
   - Use pypi-workflow-generator for CI/CD
   - Compatible with standard Python tooling
   - Works with cookiecutter/copier ecosystem

4. **Self-Hosting**
   - The generator itself is an MCP server
   - Can be used by AI agents to create new MCP servers
   - Demonstrates the pattern it generates

### Success Criteria

✅ Generate working MCP server in < 5 minutes
✅ Generated servers pass all tests
✅ Generated servers work in both MCP and CLI modes
✅ GitHub Actions workflows work out-of-box
✅ Documentation is complete and accurate
✅ AI agents can use it to create new MCP servers

---

## Reference Architecture

### Existing MCP Servers (Learning From)

**1. mcp-server-webauthn-client** (TypeScript)
- Template-based generation using Handlebars
- Dual-mode: MCP server + CLI
- Complete Docker stack generation
- 20+ template files

**2. pypi-workflow-generator** (Python - ✅ COMPLETED)
- Template-based using Jinja2
- Dual-mode: MCP server + CLI
- GitHub Actions workflow generation
- Project initialization (pyproject.toml, setup.py)
- Release management (git tagging)
- Published on PyPI: https://pypi.org/project/pypi-workflow-generator/
- Repository: https://github.com/hitoshura25/pypi-workflow-generator

### Key Learnings from pypi-workflow-generator

**What Worked Well:**
1. **Clean separation**: server.py (MCP), main.py/init.py/create_release.py (CLI), generator.py (core logic)
2. **Jinja2 templates**: Single template file per output type (workflow, pyproject.toml, setup.py)
3. **Dual entry points**: Clear naming convention (mcp- prefix for server, tool-specific for CLI)
4. **Interface flexibility**: CLI uses semantic versioning (major/minor/patch), MCP uses explicit versions
5. **Dogfooding**: Used itself to generate its own workflow - validates the tool works
6. **setuptools_scm integration**: Automatic versioning from git tags

**Architecture Pattern Validated:**
```
pypi_workflow_generator/
├── __init__.py           # Public API exports
├── server.py             # MCP stdio server (mcp-pypi-workflow-generator)
├── main.py               # CLI for workflow generation (pypi-workflow-generator)
├── init.py               # CLI for project initialization (pypi-workflow-generator-init)
├── create_release.py     # CLI for release management (pypi-release)
├── generator.py          # Core business logic (shared by all)
├── tests/
│   ├── test_server.py    # MCP protocol tests (11 tests)
│   ├── test_generator.py # Core logic tests (2 tests)
│   └── test_init.py      # Init tests (1 test)
└── *.j2                  # Jinja2 templates
```

**Best Practices Validated:**
- ✅ Template-based generation works excellently
- ✅ Dual-mode architecture is practical and maintainable
- ✅ MCP server integration is straightforward
- ✅ CLI and MCP can have different interfaces (optimized for their use cases)
- ✅ Exit code handling matters (use sys.exit(main()))
- ✅ pytest-asyncio required for async MCP tests

### Pattern We're Extracting

```
Every MCP Server Needs:
├── Dual Entry Points
│   ├── server.py (MCP stdio protocol)
│   └── cli.py (argument parsing)
├── Shared Core Logic
│   └── generator.py (business logic)
├── Package Configuration
│   ├── setup.py (metadata, dependencies)
│   ├── pyproject.toml (build system)
│   └── MANIFEST.in (include templates)
├── Testing
│   ├── test_server.py (MCP protocol tests)
│   ├── test_cli.py (CLI tests)
│   └── test_integration.py (end-to-end)
├── Documentation
│   ├── README.md (usage for both modes)
│   └── MCP-USAGE.md (MCP-specific docs)
└── CI/CD
    └── .github/workflows/pypi-publish.yml
```

---

## What Gets Generated

When you run `mcp-server-generator`, you get a complete project:

### Project Structure (Python)

```
my-awesome-mcp-server/
├── .gitignore
├── README.md
├── MCP-USAGE.md
├── LICENSE (Apache-2.0)
├── pyproject.toml
├── setup.py
├── requirements.txt
├── MANIFEST.in
│
├── my_awesome_mcp_server/
│   ├── __init__.py
│   ├── server.py          # MCP stdio server
│   ├── cli.py             # CLI interface
│   ├── generator.py       # Core business logic
│   │
│   ├── templates/         # If your MCP server generates files
│   │   └── example.j2
│   │
│   └── tests/
│       ├── __init__.py
│       ├── test_server.py
│       ├── test_cli.py
│       └── test_integration.py
│
└── .github/
    └── workflows/
        └── pypi-publish.yml  # Generated by pypi-workflow-generator!
```

### Features of Generated Project

✅ **Working MCP Server** - Responds to `tools/list` and `tools/call`
✅ **CLI Mode** - Standard argparse-based CLI
✅ **Proper Packaging** - Installable via pip
✅ **GitHub Actions** - CI/CD for PyPI publishing
✅ **Complete Tests** - Unit, integration, MCP protocol tests
✅ **Documentation** - README, MCP usage guide, examples
✅ **Type Hints** - Full type annotations
✅ **Error Handling** - Proper exception handling and logging

---

## Architecture Overview

### mcp-server-generator Architecture

```
mcp-server-generator/
├── mcp_server_generator/
│   ├── __init__.py
│   ├── server.py          # MCP server (generates MCP servers!)
│   ├── cli.py             # CLI mode
│   ├── generator.py       # Core generation logic
│   │
│   └── templates/
│       ├── python/        # Python MCP server templates
│       │   ├── __init__.py.j2
│       │   ├── server.py.j2
│       │   ├── cli.py.j2
│       │   ├── generator.py.j2
│       │   ├── setup.py.j2
│       │   ├── pyproject.toml.j2
│       │   ├── README.md.j2
│       │   ├── MCP-USAGE.md.j2
│       │   ├── requirements.txt.j2
│       │   ├── MANIFEST.in.j2
│       │   ├── .gitignore.j2
│       │   ├── LICENSE.j2
│       │   └── tests/
│       │       ├── __init__.py.j2
│       │       ├── test_server.py.j2
│       │       ├── test_cli.py.j2
│       │       └── test_integration.py.j2
│       │
│       ├── typescript/    # Future: TypeScript MCP servers
│       └── go/           # Future: Go MCP servers
```

### Dual-Mode Operation

**MCP Mode** (for AI agents):
```bash
# In claude_config.json:
{
  "mcpServers": {
    "mcp-server-generator": {
      "command": "mcp-server-generator"
    }
  }
}

# Agent can call:
generate_mcp_server({
  "project_name": "my-tool",
  "description": "A tool that does X",
  "tools": [
    {"name": "do_something", "description": "Does something"}
  ]
})
```

**CLI Mode** (for developers):
```bash
# Quick start
mcp-server-generator --project-name my-tool \
  --description "A tool that does X" \
  --author "Your Name" \
  --email "your@email.com"

# Interactive mode
mcp-server-generator --interactive

# With tool definitions from JSON
mcp-server-generator --project-name my-tool \
  --tools-file ./tools-schema.json
```

---

## Implementation Phases

### Phase 0: Prerequisites ✅ COMPLETED

**Deliverable**: Working pypi-workflow-generator
**Time**: 10-13 hours (COMPLETED)
**Status**: ✅ COMPLETED - Published to PyPI v0.2.0

**Links:**
- Repository: https://github.com/hitoshura25/pypi-workflow-generator
- PyPI Package: https://pypi.org/project/pypi-workflow-generator/
- Implementation Plan: DUAL_MODE_IMPLEMENTATION_PLAN.md

**What Was Validated**:
- ✅ Dual-mode architecture pattern works excellently
- ✅ GitHub Actions workflow generation is reliable
- ✅ Serves as proven reference implementation
- ✅ Ready to be integrated into mcp-server-generator
- ✅ Dogfooding demonstrated (generates its own workflow)
- ✅ All 15 tests passing

---

### Phase 1: Core Generator Structure

**Time Estimate**: 6-8 hours
**Priority**: CRITICAL

#### 1.1 Project Setup

**Create base project structure**:

```bash
mcp-server-generator/
├── .gitignore
├── README.md
├── LICENSE (Apache-2.0)
├── pyproject.toml
├── setup.py
├── requirements.txt
├── MANIFEST.in
└── mcp_server_generator/
    ├── __init__.py
    └── (to be created in later steps)
```

**Dependencies**:
```python
# requirements.txt
Jinja2>=3.1.0
PyYAML>=6.0
click>=8.1.0  # For better CLI
pytest>=7.0.0
pytest-asyncio>=0.21.0  # For async MCP tests
pypi-workflow-generator>=0.2.0  # ✅ Now available on PyPI!
```

**Key Files**:

**`mcp_server_generator/__init__.py`**:
```python
"""
MCP Server Generator

A meta-generator for creating dual-mode MCP servers with best practices.
"""

__version__ = "0.1.0"
__author__ = "Vinayak Menon"
__license__ = "Apache-2.0"

from .generator import (
    generate_mcp_server,
    generate_tool_schema,
    validate_project_name,
)

__all__ = [
    'generate_mcp_server',
    'generate_tool_schema',
    'validate_project_name',
]
```

#### 1.2 Core Generator Logic

**File**: `mcp_server_generator/generator.py`

**Key Functions**:

```python
"""
Core MCP server generation logic.
"""

import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import yaml


def validate_project_name(name: str) -> bool:
    """
    Validate Python package name.

    Must be:
    - Lowercase
    - Alphanumeric + underscores/hyphens
    - Not a Python keyword
    - Valid Python identifier when hyphens converted to underscores
    """
    # Convert to package name (hyphens to underscores)
    package_name = name.replace('-', '_')

    # Check valid Python identifier
    if not package_name.isidentifier():
        return False

    # Check not a keyword
    import keyword
    if keyword.iskeyword(package_name):
        return False

    return True


def generate_tool_schema(tool_definition: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate MCP tool schema from simplified definition.

    Args:
        tool_definition: {
            "name": "my_tool",
            "description": "Does something",
            "parameters": [
                {"name": "param1", "type": "string", "required": True},
                {"name": "param2", "type": "number", "required": False}
            ]
        }

    Returns:
        Full MCP tool schema with inputSchema
    """
    schema = {
        "name": tool_definition["name"],
        "description": tool_definition["description"],
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }

    for param in tool_definition.get("parameters", []):
        schema["inputSchema"]["properties"][param["name"]] = {
            "type": param["type"],
            "description": param.get("description", "")
        }

        if param.get("required", False):
            schema["inputSchema"]["required"].append(param["name"])

    return schema


def generate_mcp_server(
    project_name: str,
    description: str,
    author: str,
    author_email: str,
    tools: List[Dict[str, Any]],
    output_dir: Optional[str] = None,
    python_version: str = "3.8",
    license: str = "Apache-2.0",
    include_github_actions: bool = True,
    language: str = "python"
) -> Dict[str, Any]:
    """
    Generate a complete MCP server project.

    Args:
        project_name: Project name (e.g., "my-mcp-server")
        description: Project description
        author: Author name
        author_email: Author email
        tools: List of tool definitions
        output_dir: Where to create project (default: current directory)
        python_version: Python version for testing (default: "3.8")
        license: License type (default: "Apache-2.0")
        include_github_actions: Include CI/CD workflow (default: True)
        language: Target language (default: "python")

    Returns:
        {
            "success": bool,
            "project_path": str,
            "files_created": List[str],
            "message": str
        }
    """
    # Validate inputs
    if not validate_project_name(project_name):
        raise ValueError(f"Invalid project name: {project_name}")

    if language not in ["python"]:  # Add more later
        raise ValueError(f"Unsupported language: {language}")

    # Convert project name to package name
    package_name = project_name.replace('-', '_')

    # Determine output directory
    if output_dir is None:
        output_dir = os.getcwd()

    project_path = os.path.join(output_dir, project_name)

    # Check if directory exists
    if os.path.exists(project_path):
        raise FileExistsError(f"Directory already exists: {project_path}")

    # Get template directory
    template_dir = os.path.join(
        os.path.dirname(__file__),
        'templates',
        language
    )

    if not os.path.exists(template_dir):
        raise FileNotFoundError(f"Templates not found for {language}")

    # Prepare template context
    context = {
        'project_name': project_name,
        'package_name': package_name,
        'description': description,
        'author': author,
        'author_email': author_email,
        'python_version': python_version,
        'license': license,
        'tools': tools,
        'tool_schemas': [generate_tool_schema(tool) for tool in tools],
        'year': '2025',  # Or use datetime.now().year
    }

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(template_dir))

    # Files to generate
    files_to_generate = [
        # Root files
        ('README.md.j2', 'README.md'),
        ('MCP-USAGE.md.j2', 'MCP-USAGE.md'),
        ('LICENSE.j2', 'LICENSE'),
        ('setup.py.j2', 'setup.py'),
        ('pyproject.toml.j2', 'pyproject.toml'),
        ('requirements.txt.j2', 'requirements.txt'),
        ('MANIFEST.in.j2', 'MANIFEST.in'),
        ('.gitignore.j2', '.gitignore'),

        # Package files
        ('__init__.py.j2', f'{package_name}/__init__.py'),
        ('server.py.j2', f'{package_name}/server.py'),
        ('cli.py.j2', f'{package_name}/cli.py'),
        ('generator.py.j2', f'{package_name}/generator.py'),

        # Tests
        ('tests/__init__.py.j2', f'{package_name}/tests/__init__.py'),
        ('tests/test_server.py.j2', f'{package_name}/tests/test_server.py'),
        ('tests/test_cli.py.j2', f'{package_name}/tests/test_cli.py'),
        ('tests/test_integration.py.j2', f'{package_name}/tests/test_integration.py'),
    ]

    files_created = []

    # Generate files
    for template_file, output_file in files_to_generate:
        template = env.get_template(template_file)
        content = template.render(**context)

        output_path = os.path.join(project_path, output_file)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(content)

        files_created.append(output_file)

    # Generate GitHub Actions workflow if requested
    if include_github_actions:
        # Use pypi-workflow-generator! (✅ Now fully tested and available on PyPI)
        try:
            from pypi_workflow_generator import generate_workflow

            # Change to project directory temporarily
            original_dir = os.getcwd()
            os.chdir(project_path)

            try:
                workflow_result = generate_workflow(
                    python_version=python_version,
                    output_filename='pypi-publish.yml',
                    release_on_main_push=False,  # Conservative default
                    test_path=package_name,
                    verbose_publish=True  # Helpful for debugging
                )

                if workflow_result['success']:
                    files_created.append('.github/workflows/pypi-publish.yml')

                    # Also initialize project files if needed
                    from pypi_workflow_generator import initialize_project
                    # (optional integration for complete setup)

            finally:
                os.chdir(original_dir)

        except ImportError:
            # Graceful fallback if pypi-workflow-generator not installed
            print("Warning: pypi-workflow-generator not found. Skipping workflow generation.")
            print("Install with: pip install pypi-workflow-generator>=0.2.0")

    return {
        'success': True,
        'project_path': project_path,
        'files_created': files_created,
        'message': f"Successfully generated MCP server project at {project_path}"
    }
```

#### 1.3 Success Criteria for Phase 1

✅ Project structure created
✅ Core generator logic implemented
✅ Validation functions working
✅ Tool schema generation working
✅ Basic tests passing

---

### Phase 2: Template Development

**Time Estimate**: 8-10 hours
**Priority**: HIGH

#### 2.1 Python Server Template

**File**: `mcp_server_generator/templates/python/server.py.j2`

```python
#!/usr/bin/env python3
"""
MCP Server for {{ project_name }}.

{{ description }}
"""

import sys
import json
import asyncio
from typing import Any, Dict

from .generator import {{ tools|map(attribute='name')|join(', ') }}


class MCPServer:
    """MCP server implementation for {{ project_name }}."""

    def __init__(self):
        self.name = "{{ package_name }}"
        self.version = "1.0.0"

    async def handle_list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return {
            "tools": {{ tool_schemas | tojson(indent=16) }}
        }

    async def handle_call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool."""
        try:
            {% for tool in tools %}
            if tool_name == "{{ tool.name }}":
                result = {{ tool.name }}(**arguments)
                return {
                    "content": [{"type": "text", "text": str(result)}],
                    "isError": False
                }
            {% endfor %}

            return {
                "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}],
                "isError": True
            }

        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request."""
        method = request.get("method")
        params = request.get("params", {})

        if method == "tools/list":
            return await self.handle_list_tools()
        elif method == "tools/call":
            return await self.handle_call_tool(
                params.get("name"),
                params.get("arguments", {})
            )
        else:
            return {
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    async def run(self):
        """Run MCP server on stdio."""
        print(f"{{ project_name }} MCP server running", file=sys.stderr)

        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                request = json.loads(line)
                response = await self.handle_request(request)

                if "id" in request:
                    response["id"] = request["id"]

                print(json.dumps(response), flush=True)

            except json.JSONDecodeError as e:
                error_response = {
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                error_response = {
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                }
                print(json.dumps(error_response), flush=True)


def main():
    """Main entry point."""
    server = MCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
```

#### 2.2 Python CLI Template

**File**: `mcp_server_generator/templates/python/cli.py.j2`

```python
#!/usr/bin/env python3
"""
CLI for {{ project_name }}.

{{ description }}
"""

import argparse
from .generator import {{ tools|map(attribute='name')|join(', ') }}


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='{{ description }}')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    {% for tool in tools %}
    # {{ tool.name }} command
    {{ tool.name }}_parser = subparsers.add_parser(
        '{{ tool.name }}',
        help='{{ tool.description }}'
    )
    {% for param in tool.parameters %}
    {{ tool.name }}_parser.add_argument(
        '--{{ param.name }}',
        type={{ 'str' if param.type == 'string' else param.type }},
        {% if param.required %}required=True,{% endif %}
        help='{{ param.description }}'
    )
    {% endfor %}

    {% endfor %}

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    try:
        {% for tool in tools %}
        if args.command == '{{ tool.name }}':
            result = {{ tool.name }}(
                {% for param in tool.parameters %}
                {{ param.name }}=args.{{ param.name }}{{ ',' if not loop.last else '' }}
                {% endfor %}
            )
            print(result)
        {% endfor %}

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit(main())
```

#### 2.3 Python Generator Template (Business Logic)

**File**: `mcp_server_generator/templates/python/generator.py.j2`

```python
"""
Core business logic for {{ project_name }}.

{{ description }}
"""

from typing import Any, Dict

{% for tool in tools %}

def {{ tool.name }}(
    {% for param in tool.parameters %}
    {{ param.name }}: {{ 'str' if param.type == 'string' else param.type }}{{ ' = None' if not param.required else '' }}{{ ',' if not loop.last else '' }}
    {% endfor %}
) -> Dict[str, Any]:
    """
    {{ tool.description }}

    Args:
        {% for param in tool.parameters %}
        {{ param.name }}: {{ param.description }}
        {% endfor %}

    Returns:
        Result dictionary
    """
    # TODO: Implement {{ tool.name }} logic
    return {
        'success': True,
        'message': 'TODO: Implement {{ tool.name }}'
    }

{% endfor %}
```

#### 2.4 README Template

**File**: `mcp_server_generator/templates/python/README.md.j2`

```markdown
# {{ project_name }}

{{ description }}

## Installation

```bash
pip install {{ project_name }}
```

## Usage

### MCP Mode (For AI Agents)

Add to `claude_config.json`:

```json
{
  "mcpServers": {
    "{{ package_name }}": {
      "command": "mcp-{{ project_name }}"
    }
  }
}
```

### CLI Mode (For Developers)

{% for tool in tools %}
**{{ tool.name }}**: {{ tool.description }}

```bash
{{ project_name }} {{ tool.name }} {% for param in tool.parameters %}--{{ param.name }} <value> {% endfor %}
```
{% endfor %}

## Available Tools

{% for tool in tools %}
### {{ tool.name }}

{{ tool.description }}

**Parameters:**
{% for param in tool.parameters %}
- `{{ param.name }}` ({{ param.type }}{% if param.required %}, required{% endif %}): {{ param.description }}
{% endfor %}

{% endfor %}

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Build package
python -m build
```

## License

{{ license }}
```

#### 2.5 Setup.py Template

**File**: `mcp_server_generator/templates/python/setup.py.j2`

```python
from setuptools import setup, find_packages
import os

def local_scheme(version):
    if os.environ.get("IS_PULL_REQUEST"):
        return f".dev{os.environ.get('GITHUB_RUN_ID', 'local')}"
    return ""

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = ""

setup(
    name='{{ project_name }}',
    author='{{ author }}',
    author_email='{{ author_email }}',
    description='{{ description }}',
    url='https://github.com/{{ author }}/{{ project_name }}',  # Update with real URL
    use_scm_version={"local_scheme": local_scheme},
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Add your dependencies here
    ],
    python_requires='>={{ python_version }}',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            '{{ project_name }}={{ package_name }}.cli:main',
            'mcp-{{ project_name }}={{ package_name }}.server:main',
        ],
    },
)
```

#### 2.6 Success Criteria for Phase 2

✅ All templates created
✅ Templates render correctly with test data
✅ Generated code is valid Python
✅ No syntax errors in templates

---

### Phase 3: CLI and MCP Server Implementation

**Time Estimate**: 4-6 hours
**Priority**: HIGH

#### 3.1 CLI Implementation

**File**: `mcp_server_generator/cli.py`

```python
#!/usr/bin/env python3
"""
CLI for MCP Server Generator.
"""

import argparse
import json
import sys
from pathlib import Path
from .generator import generate_mcp_server, validate_project_name


def load_tools_from_file(filepath: str):
    """Load tool definitions from JSON/YAML file."""
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Tools file not found: {filepath}")

    with open(path) as f:
        if filepath.endswith('.json'):
            return json.load(f)
        elif filepath.endswith(('.yaml', '.yml')):
            import yaml
            return yaml.safe_load(f)
        else:
            raise ValueError("Tools file must be .json, .yaml, or .yml")


def interactive_mode():
    """Interactive project creation."""
    print("=== MCP Server Generator - Interactive Mode ===\n")

    project_name = input("Project name (e.g., my-mcp-server): ").strip()
    while not validate_project_name(project_name):
        print("Invalid project name. Use lowercase, alphanumeric, hyphens/underscores only.")
        project_name = input("Project name: ").strip()

    description = input("Description: ").strip()
    author = input("Author name: ").strip()
    author_email = input("Author email: ").strip()

    print("\nDefine your tools (empty name to finish):")
    tools = []

    while True:
        tool_name = input(f"\nTool #{len(tools) + 1} name (or press Enter to finish): ").strip()
        if not tool_name:
            break

        tool_desc = input(f"  Description for {tool_name}: ").strip()

        print(f"  Parameters for {tool_name} (empty name to finish):")
        parameters = []

        while True:
            param_name = input(f"    Parameter name (or press Enter to finish): ").strip()
            if not param_name:
                break

            param_type = input(f"    Type for {param_name} (string/number/boolean): ").strip()
            param_desc = input(f"    Description for {param_name}: ").strip()
            param_required = input(f"    Required? (y/n): ").strip().lower() == 'y'

            parameters.append({
                "name": param_name,
                "type": param_type,
                "description": param_desc,
                "required": param_required
            })

        tools.append({
            "name": tool_name,
            "description": tool_desc,
            "parameters": parameters
        })

    if not tools:
        print("\nError: At least one tool must be defined.")
        return 1

    print(f"\nGenerating MCP server '{project_name}' with {len(tools)} tool(s)...")

    try:
        result = generate_mcp_server(
            project_name=project_name,
            description=description,
            author=author,
            author_email=author_email,
            tools=tools
        )

        print(f"\n✅ {result['message']}")
        print(f"\nFiles created:")
        for file in result['files_created']:
            print(f"  - {file}")

        print(f"\nNext steps:")
        print(f"  1. cd {project_name}")
        print(f"  2. pip install -r requirements.txt")
        print(f"  3. pytest")
        print(f"  4. Implement tool logic in {project_name.replace('-', '_')}/generator.py")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate MCP servers with dual-mode architecture'
    )

    parser.add_argument('--project-name', help='Project name (e.g., my-mcp-server)')
    parser.add_argument('--description', help='Project description')
    parser.add_argument('--author', help='Author name')
    parser.add_argument('--email', help='Author email')
    parser.add_argument('--tools-file', help='JSON/YAML file with tool definitions')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--output-dir', help='Output directory (default: current directory)')
    parser.add_argument('--python-version', default='3.8', help='Python version (default: 3.8)')
    parser.add_argument('--no-github-actions', action='store_true', help='Skip GitHub Actions workflow')

    args = parser.parse_args()

    # Interactive mode
    if args.interactive:
        return interactive_mode()

    # Validate required arguments for non-interactive mode
    if not all([args.project_name, args.description, args.author, args.email, args.tools_file]):
        parser.error("--project-name, --description, --author, --email, and --tools-file are required (or use --interactive)")

    try:
        # Load tools
        tools_data = load_tools_from_file(args.tools_file)
        tools = tools_data if isinstance(tools_data, list) else tools_data.get('tools', [])

        # Generate server
        result = generate_mcp_server(
            project_name=args.project_name,
            description=args.description,
            author=args.author,
            author_email=args.email,
            tools=tools,
            output_dir=args.output_dir,
            python_version=args.python_version,
            include_github_actions=not args.no_github_actions
        )

        print(result['message'])
        print(f"\nFiles created:")
        for file in result['files_created']:
            print(f"  - {file}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit(main())
```

#### 3.2 MCP Server Implementation

**File**: `mcp_server_generator/server.py`

Similar structure to pypi-workflow-generator server, exposing:
- `generate_mcp_server` tool
- `validate_project_name` tool (utility)

#### 3.3 Success Criteria for Phase 3

✅ CLI works in both modes (arguments and interactive)
✅ MCP server responds to tool calls
✅ Tool definitions from JSON/YAML work
✅ Error handling works correctly

---

### Phase 4: Testing

**Time Estimate**: 3-4 hours
**Priority**: HIGH

#### Test Files

1. `test_generator.py` - Test core generation logic
2. `test_server.py` - Test MCP server
3. `test_cli.py` - Test CLI
4. `test_integration.py` - End-to-end tests
5. `test_templates.py` - Template rendering tests

#### Key Tests

```python
def test_generates_valid_python_project(tmp_path):
    """Test that generated project is valid Python."""
    result = generate_mcp_server(
        project_name="test-server",
        description="Test",
        author="Test",
        author_email="test@example.com",
        tools=[{
            "name": "test_tool",
            "description": "Test tool",
            "parameters": []
        }],
        output_dir=str(tmp_path),
        include_github_actions=False
    )

    assert result['success']

    # Verify structure
    project_dir = tmp_path / "test-server"
    assert (project_dir / "setup.py").exists()
    assert (project_dir / "test_server" / "__init__.py").exists()
    assert (project_dir / "test_server" / "server.py").exists()

    # Verify Python syntax
    import py_compile
    for py_file in project_dir.rglob("*.py"):
        py_compile.compile(str(py_file), doraise=True)
```

---

### Phase 5: Documentation

**Time Estimate**: 2-3 hours
**Priority**: MEDIUM

#### Documentation Files

1. **README.md** - Main usage guide
2. **MCP-USAGE.md** - MCP-specific documentation
3. **TEMPLATE-GUIDE.md** - Template development guide
4. **CONTRIBUTING.md** - Contribution guidelines

---

### Phase 6: Integration & Polish

**Time Estimate**: 2-3 hours
**Priority**: MEDIUM

#### 6.1 pypi-workflow-generator Integration

Ensure seamless integration:
- Import works correctly
- Workflows generate successfully
- Error handling for missing pypi-workflow-generator

#### 6.2 Polish

- Better error messages
- Progress indicators
- Validation improvements
- CLI help improvements

---

## Tool Schema

### MCP Server Tools

```typescript
{
  "tools": [
    {
      "name": "generate_mcp_server",
      "description": "Generate a complete MCP server project with dual-mode architecture",
      "inputSchema": {
        "type": "object",
        "properties": {
          "project_name": {
            "type": "string",
            "description": "Project name (e.g., 'my-mcp-server')"
          },
          "description": {
            "type": "string",
            "description": "Project description"
          },
          "author": {
            "type": "string",
            "description": "Author name"
          },
          "author_email": {
            "type": "string",
            "description": "Author email"
          },
          "tools": {
            "type": "array",
            "description": "List of tools this MCP server will provide",
            "items": {
              "type": "object",
              "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "parameters": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "name": {"type": "string"},
                      "type": {"type": "string"},
                      "description": {"type": "string"},
                      "required": {"type": "boolean"}
                    }
                  }
                }
              }
            }
          },
          "python_version": {
            "type": "string",
            "description": "Python version (default: 3.8)"
          },
          "include_github_actions": {
            "type": "boolean",
            "description": "Include GitHub Actions workflow (default: true)"
          }
        },
        "required": ["project_name", "description", "author", "author_email", "tools"]
      }
    }
  ]
}
```

---

## Timeline Summary

| Phase | Description | Time | Status |
|-------|-------------|------|--------|
| Phase 0 | Complete pypi-workflow-generator | 10-13 hrs | ✅ COMPLETED |
| Phase 1 | Core generator structure | 6-8 hrs | 🎯 Ready to start |
| Phase 2 | Template development | 8-10 hrs | Pending |
| Phase 3 | CLI and MCP server | 4-6 hrs | Pending |
| Phase 4 | Testing | 3-4 hrs | Pending |
| Phase 5 | Documentation | 2-3 hrs | Pending |
| Phase 6 | Integration & polish | 2-3 hrs | Pending |
| **Total** | **Full implementation** | **35-47 hrs** | **In Progress** |

**With Phase 0 COMPLETED ✅**: 25-34 hours remaining

**Next Steps:**
1. ✅ pypi-workflow-generator completed and published to PyPI v0.2.0
2. 🎯 Begin Phase 1 immediately - foundation is ready
3. 📅 Target completion: 25-34 hours of focused development
4. 🔗 Leverage completed reference implementation for patterns and examples

---

## Lessons Learned from pypi-workflow-generator

### Architecture Decisions

**✅ What Worked:**
1. **Separate CLI files**: main.py, init.py, create_release.py instead of one giant CLI
2. **Single template file per output**: One Jinja2 template is sufficient for focused tools
3. **Flexible interfaces**: Different APIs for CLI vs MCP (optimized for each use case)
4. **Entry point naming**: `mcp-` prefix for server, tool-specific prefixes for CLI
5. **Shared core logic**: generator.py used by all entry points eliminates code duplication

**⚠️ What to Improve:**
1. **Template discovery**: Need better template path resolution (used package_resources)
2. **Error messages**: More specific error messages for common failures
3. **Validation**: Add upfront validation for all inputs before processing
4. **Documentation**: Inline comments in generated files help users understand output

### Testing Insights

**✅ Effective Test Patterns:**
- MCP protocol tests (request/response validation)
- Template rendering tests with temporary directories
- Integration tests using pytest tmp_path fixture
- Dogfooding (using tool on itself) - validates end-to-end

**Test Suite Statistics:**
- 15 total tests (11 MCP server, 2 generator, 1 init, 1 release)
- All tests use pytest with pytest-asyncio for async MCP tests
- Clean separation: test_server.py, test_generator.py, test_init.py

**Patterns to Replicate:**
```python
def test_mcp_protocol():
    """Test MCP stdio protocol compliance."""
    # Send tools/list request
    # Validate response schema
    # Test each tool's inputSchema

def test_template_generation(tmp_path):
    """Test template renders correctly."""
    # Use tmp_path fixture
    # Render template with mock context
    # Validate output syntax and content
```

### Distribution Learnings

**What We Learned:**
- **setuptools_scm** works great for automatic versioning from git tags
- **Trusted Publishers** simplify PyPI publishing (no API tokens needed)
- **GitHub Actions** workflow is reliable for automated releases
- **TestPyPI** testing catches packaging issues early
- **Entry points** in setup.py create proper executable scripts
- **MANIFEST.in** required to include template files in distribution

**Build Configuration:**
```toml
[build-system]
requires = ["setuptools>=61.0", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[tool.setuptools_scm]
version_scheme = "post-release"
```

### Code Quality

**Best Practices Validated:**
- ✅ Type hints improve code clarity and IDE support
- ✅ Exit code handling matters (use `sys.exit(main())`)
- ✅ Docstrings at module and function level
- ✅ Consistent error handling with try/except
- ✅ Pythonic assertions (`assert result['success']` not `== True`)

---

## Integration with pypi-workflow-generator

### Example 1: Basic Integration

When generating an MCP server, automatically set up complete CI/CD:

```python
# In mcp_server_generator/generator.py
from pypi_workflow_generator import (
    generate_workflow,
    initialize_project,
)

def generate_complete_mcp_project(
    project_name: str,
    package_name: str,
    author: str,
    author_email: str,
    description: str,
    python_version: str = "3.11",
    include_ci_cd: bool = True,
    **kwargs
) -> dict:
    """Generate complete MCP server project with CI/CD setup."""

    # 1. Create project structure
    project_path = create_project_structure(project_name, package_name)

    if include_ci_cd:
        os.chdir(project_path)

        # 2. Initialize PyPI configuration
        init_result = initialize_project(
            package_name=package_name,
            author=author,
            author_email=author_email,
            description=description,
            url=f"https://github.com/{author}/{project_name}",
            command_name=package_name.replace('_', '-')
        )

        # 3. Generate GitHub Actions workflow
        workflow_result = generate_workflow(
            python_version=python_version,
            test_path=package_name,
            verbose_publish=True
        )

        return {
            'success': True,
            'project_path': project_path,
            'files_created': init_result['files_created'] + [workflow_result['file_path']]
        }
```

### Example 2: Template Integration

Reference pypi-workflow-generator in generated README:

```markdown
# In templates/python/README.md.j2

## Publishing to PyPI

This project uses [pypi-workflow-generator](https://github.com/hitoshura25/pypi-workflow-generator)
for automated PyPI publishing via GitHub Actions.

### Create a Release

```bash
# Install pypi-workflow-generator if not already installed
pip install pypi-workflow-generator>=0.2.0

# Create and push a release tag
pypi-release patch  # or minor, major
```

### What Happens Next

1. Creates version tag (e.g., v1.0.1)
2. Pushes tag to GitHub
3. GitHub Actions automatically:
   - Runs tests
   - Builds package
   - Publishes to PyPI
4. Uses Trusted Publishers (no API tokens needed!)
```

### Example 3: Progressive Enhancement

Allow users to add CI/CD later:

```markdown
# In generated project's README.md

## Add CI/CD Later

If you skipped GitHub Actions during generation, add it anytime:

```bash
pip install pypi-workflow-generator
cd your-project
pypi-workflow-generator --python-version 3.11 --test-path your_package
```

This creates `.github/workflows/pypi-publish.yml` for automated PyPI publishing.
```

### Example 4: MCP Configuration in Generated Docs

Include MCP setup instructions in generated documentation:

```markdown
# In templates/python/MCP-USAGE.md.j2

## Development Setup

After generating this MCP server, you can generate its CI/CD workflow:

```bash
# Install the workflow generator
pip install pypi-workflow-generator

# Generate GitHub Actions workflow
pypi-workflow-generator \
  --python-version {{ python_version }} \
  --test-path {{ package_name }}

# Create your first release
pypi-release patch
```

The workflow generator is itself an MCP server! You can use it programmatically:

```json
{
  "mcpServers": {
    "pypi-workflow-gen": {
      "command": "mcp-pypi-workflow-generator"
    }
  }
}
```
```

### Real-World Example

The pypi-workflow-generator **dogfoods itself**:

```bash
# The actual command used to generate its own workflow
pypi-workflow-generator \
  --python-version 3.11 \
  --test-path pypi_workflow_generator/ \
  --verbose-publish
```

This generated workflow has been successfully used to:
- ✅ Publish v0.1.0 to PyPI
- ✅ Publish v0.1.1 with bug fixes
- ✅ Publish v0.2.0 with new features

**Workflow file header:**
```yaml
# This workflow was generated by pypi-workflow-generator (dogfooding!)
# Command: pypi-workflow-generator --python-version 3.11 --test-path pypi_workflow_generator/ --verbose-publish
```

This proves the tool works reliably!

---

## Future Enhancements

### Version 2.0

- **TypeScript Support**: Generate TypeScript MCP servers
- **Go Support**: Generate Go MCP servers
- **Template Updates**: Use Copier for template updating
- **Tool Library**: Pre-built tool templates (file ops, API calls, etc.)
- **Docker Support**: Generate Dockerfiles and compose files
- **Advanced Testing**: Generate E2E test suites

### Version 3.0

- **GUI**: Web-based project generator
- **Template Marketplace**: Community templates
- **Multi-tool Projects**: Servers with multiple tool types
- **Cloud Deployment**: Generate cloud deployment configs

---

## Success Metrics

**Phase 1 Success**:
- Generated server installs without errors
- Tests pass
- Both modes (CLI + MCP) work

**Phase 2 Success**:
- 10+ MCP servers generated using this tool
- Community adoption
- Positive feedback from users

**Long-term Success**:
- Standard tool for MCP server development
- Active community contributions
- Used by major AI agents

---

## Risks and Mitigation

### Risk 1: Template Complexity
**Mitigation**: Start simple, iterate based on real usage

### Risk 2: pypi-workflow-generator Integration Issues
**Mitigation**: Thorough integration testing, fallback options

### Risk 3: Changing MCP Spec
**Mitigation**: Version templates, support multiple MCP versions

---

## Next Steps

1. ✅ Complete pypi-workflow-generator (per DUAL_MODE_IMPLEMENTATION_PLAN.md)
2. ⏸️ Review this plan
3. 🚀 Begin Phase 1 of mcp-server-generator

---

**Document Version**: 1.0
**Created**: 2025-10-31
**Status**: Planning (awaiting pypi-workflow-generator completion)
**Estimated Start Date**: After pypi-workflow-generator ships
