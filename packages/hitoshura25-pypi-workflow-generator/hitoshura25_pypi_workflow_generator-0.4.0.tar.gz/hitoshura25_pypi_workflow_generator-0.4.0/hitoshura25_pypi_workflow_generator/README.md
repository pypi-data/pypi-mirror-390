# `hitoshura25_pypi_workflow_generator` Package

Core logic for generating GitHub Actions workflows for Python packages.

## Architecture

This package implements a dual-mode architecture:

```
Entry Points:
├── server.py         → MCP server (for AI agents)
├── main.py           → CLI workflow generator
├── init.py           → Project initialization CLI
└── create_release.py → Release management CLI

Shared Core:
└── generator.py      → Business logic (used by all modes)

Templates:
├── pypi_publish.yml.j2  → GitHub Actions workflow template
├── setup.py.j2          → setup.py template
└── pyproject.toml.j2    → pyproject.toml template
```

## Modules

### `generator.py`

Core business logic with reusable functions:

**Functions**:
- `generate_workflow()` - Generate GitHub Actions workflow
  - Returns: `{"success": bool, "file_path": str, "message": str}`
- `initialize_project()` - Create pyproject.toml and setup.py
  - Returns: `{"success": bool, "files_created": list, "message": str}`
- `create_git_release()` - Create and push git tags
  - Returns: `{"success": bool, "version": str, "message": str}`

All functions return dictionaries with consistent structure for easy consumption by both CLI and MCP modes.

### `server.py`

MCP server implementation:

- Implements stdio-based MCP protocol
- Provides tools for AI agents
- Wraps generator functions with MCP response format
- Handles JSON-RPC requests and responses
- Error handling with MCP-compliant format

**Entry Point**: `mcp-pypi-workflow-generator`

### `main.py`

Command-line interface for workflow generation:

- Argument parsing with argparse
- User-friendly error messages
- Wraps `generate_workflow()` for CLI use
- Supports legacy `--mcp-input` flag (deprecated)

**Entry Point**: `pypi-workflow-generator`

### `init.py`

Project initialization CLI:

- Creates pyproject.toml and setup.py
- Requires all project metadata as arguments
- Wraps `initialize_project()` for CLI use

**Entry Point**: `pypi-workflow-generator-init`

### `create_release.py`

Release management CLI:

- Creates git tags with version bumping
- Supports major/minor/patch increments
- Optional tag overwriting
- Pushes tags to remote
- Wraps `create_git_release()` for CLI use

**Entry Point**: `pypi-release`

## Templates

### `pypi_publish.yml.j2`

Jinja2 template for GitHub Actions workflow.

**Variables**:
- `python_version` - Python version (e.g., "3.11")
- `release_on_main_push` - Boolean for main branch triggering
- `test_path` - Path to tests directory
- `verbose_publish` - Boolean for verbose publishing

**Features**:
- Trusted Publishers authentication
- TestPyPI publishing on PRs
- PyPI publishing on tags
- setuptools_scm versioning

### `setup.py.j2`

Jinja2 template for setup.py.

**Variables**:
- `package_name` - Package name
- `author` - Author name
- `author_email` - Author email
- `description` - Package description
- `url` - Project URL
- `command_name` - CLI command entry point

**Features**:
- setuptools_scm integration
- PR-specific version scheme
- Dynamic README loading

### `pyproject.toml.j2`

Jinja2 template for pyproject.toml.

**Variables**: None (static template)

**Features**:
- setuptools build system
- setuptools_scm configuration
- post-release versioning scheme

## Usage Examples

### As Library

```python
from hitoshura25_pypi_workflow_generator import generate_workflow, initialize_project, create_git_release

# Initialize project
result = initialize_project(
    package_name="my-package",
    author="Your Name",
    author_email="your@email.com",
    description="My package",
    url="https://github.com/user/repo",
    command_name="my-cmd"
)
print(result['message'])

# Generate workflow
result = generate_workflow(
    python_version="3.11",
    release_on_main_push=False
)
print(result['message'])

# Create release
result = create_git_release(version="v1.0.0")
print(result['message'])
```

### MCP Mode

```bash
# Starts stdio server for AI agents
mcp-pypi-workflow-generator
```

### CLI Mode

```bash
# Initialize project
pypi-workflow-generator-init \
  --package-name my-pkg \
  --author "Name" \
  --author-email "email@example.com" \
  --description "Description" \
  --url "https://github.com/user/repo" \
  --command-name my-cmd

# Generate workflow
pypi-workflow-generator --python-version 3.11

# Create release
pypi-release patch
```

## Testing

Run the test suite:

```bash
pytest pypi_workflow_generator/tests/
```

**Test Coverage**:
- `test_generator.py` - Core generator functions
- `test_init.py` - Project initialization
- `test_server.py` - MCP server functionality

## Development

### Adding New Features

1. **Add core logic to `generator.py`**
   - Write pure Python functions
   - Return dictionaries with consistent structure
   - Handle errors gracefully

2. **Expose via CLI** (if needed)
   - Create new CLI module or extend existing
   - Add argparse configuration
   - Call generator function

3. **Expose via MCP** (if needed)
   - Update `server.py` tool definitions
   - Add tool handler in `handle_call_tool()`
   - Format response for MCP protocol

4. **Add tests**
   - Unit tests in `tests/test_generator.py`
   - MCP tests in `tests/test_server.py`

### File Locations

- Source code: `pypi_workflow_generator/`
- Tests: `pypi_workflow_generator/tests/`
- Templates: `pypi_workflow_generator/*.j2`
- Documentation: `../README.md`, `../MCP-USAGE.md`

## Dependencies

- `Jinja2>=3.0` - Template rendering
- `setuptools>=61.0` - Package building
- `setuptools_scm>=6.2` - Git-based versioning

## License

Apache-2.0
