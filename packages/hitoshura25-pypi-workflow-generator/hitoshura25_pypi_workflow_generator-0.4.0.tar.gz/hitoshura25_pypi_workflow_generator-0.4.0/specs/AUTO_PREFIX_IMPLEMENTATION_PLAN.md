# IMPLEMENTATION PLAN: Auto-Prefix Package Names with Git Username

**Date:** 2025-11-05
**Feature:** Automatic package name prefixing using git username
**Goal:** Make PyPI naming best practices automatic and friction-free

---

## Overview

Add an optional `--prefix` parameter that:
1. **Auto-detects** from git config if not provided
2. **Prepends** to package name: `{prefix}-{package_name}`
3. **Fails gracefully** if no git config and no prefix provided

Since this tool generates **GitHub Actions workflows**, we can reasonably expect users to have git configured.

---

## Design Decisions

### 1. Parameter Name: `--prefix`

**Simple and clear:**
```bash
pypi-workflow-generator-init \
  --package-name coolapp \
  --prefix myorg
# Results in PyPI package: myorg-coolapp
```

### 2. Auto-Detection from Git Config

**Priority order for auto-detection:**

```bash
# 1. Try github.user (most specific)
git config --get github.user
# Example: "jsmith"

# 2. Try GitHub username from remote URL (more reliable)
git remote get-url origin
# Example: "git@github.com:jsmith/repo.git" → extract "jsmith"

# 3. Try user.name (fallback)
git config --get user.name
# Example: "John Smith" → convert to "jsmith"

# 4. Fail with helpful error if none exist
```

### 3. Name Sanitization Rules

Convert git username to valid PyPI prefix:

```python
def sanitize_prefix(username: str) -> str:
    """
    Convert git username to valid PyPI prefix.

    Rules:
    - Lowercase
    - Replace spaces with hyphens
    - Remove special characters except hyphens
    - Remove leading/trailing hyphens

    Examples:
        "John Smith" → "john-smith"
        "jsmith@company.com" → "jsmith"
        "alice_dev" → "alice-dev"
        "Bob's Packages" → "bobs-packages"
    """
    prefix = username.lower()
    prefix = prefix.split('@')[0]  # Remove email domain if present
    prefix = re.sub(r'[^a-z0-9-]+', '-', prefix)  # Replace invalid chars
    prefix = prefix.strip('-')  # Remove leading/trailing hyphens
    return prefix
```

### 4. Behavior Options

**Option A: Always Auto-Prefix (Opinionated)** ⭐ **RECOMMENDED**

```bash
# Without --prefix, auto-detects
pypi-workflow-generator-init --package-name coolapp
# Detects git user: "jsmith"
# Creates: jsmith-coolapp

# With --prefix, uses provided value
pypi-workflow-generator-init --package-name coolapp --prefix myorg
# Creates: myorg-coolapp

# To skip prefix, use special flag
pypi-workflow-generator-init --package-name coolapp --no-prefix
# Creates: coolapp (no prefix)
```

**Pros:**
- ✅ Encourages best practices by default
- ✅ Users get proper naming without thinking about it
- ✅ Can opt-out with `--no-prefix`

**Cons:**
- ⚠️ Opinionated (forces naming convention)
- ⚠️ Might surprise users expecting exact name

**Option B: Opt-In Prefix (Less Opinionated)**

```bash
# Without --prefix or --auto-prefix, no prefix
pypi-workflow-generator-init --package-name coolapp
# Creates: coolapp

# With --auto-prefix, detects from git
pypi-workflow-generator-init --package-name coolapp --auto-prefix
# Creates: jsmith-coolapp

# With --prefix, uses provided value
pypi-workflow-generator-init --package-name coolapp --prefix myorg
# Creates: myorg-coolapp
```

**Pros:**
- ✅ Less opinionated
- ✅ Explicit opt-in

**Cons:**
- ⚠️ Users might not discover feature
- ⚠️ Won't adopt best practices by default

### 5. **RECOMMENDATION: Option A (Always Auto-Prefix)**

Since:
- This tool is for **publishing to PyPI** (where naming conflicts are real)
- PyPI best practices recommend prefixing
- Users who want no prefix can explicitly opt-out
- Better to be opinionated towards good practices

---

## Implementation Details

### 1. Add Git Username Detection

**New function in `vmenon25_pypi_workflow_generator/git_utils.py`:**

```python
"""Git utility functions."""
import subprocess
import re
from typing import Optional


def get_git_username() -> Optional[str]:
    """
    Get git username from config or remote URL.

    Tries in order:
    1. github.user (most specific)
    2. GitHub username from remote URL (more reliable)
    3. user.name (sanitized fallback)

    Returns:
        Git username or None if not found
    """
    try:
        # Try github.user first (most specific)
        result = subprocess.run(
            ['git', 'config', '--get', 'github.user'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()

        # Try extracting from GitHub remote URL
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            url = result.stdout.strip()
            # Parse https://github.com/username/repo.git
            # or git@github.com:username/repo.git
            match = re.search(r'github\.com[/:]([^/]+)/', url)
            if match:
                return match.group(1)

        # Fallback to user.name
        result = subprocess.run(
            ['git', 'config', '--get', 'user.name'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()

    except FileNotFoundError:
        # Git not installed
        pass

    return None


def sanitize_prefix(username: str) -> str:
    """
    Convert git username to valid PyPI prefix.

    Args:
        username: Raw git username

    Returns:
        Sanitized prefix suitable for PyPI

    Examples:
        >>> sanitize_prefix("John Smith")
        'john-smith'
        >>> sanitize_prefix("jsmith@company.com")
        'jsmith'
        >>> sanitize_prefix("alice_dev")
        'alice-dev'
    """
    # Lowercase
    prefix = username.lower()

    # Remove email domain if present
    if '@' in prefix:
        prefix = prefix.split('@')[0]

    # Replace invalid characters with hyphens
    prefix = re.sub(r'[^a-z0-9-]+', '-', prefix)

    # Remove leading/trailing hyphens and consecutive hyphens
    prefix = re.sub(r'-+', '-', prefix)  # Collapse multiple hyphens
    prefix = prefix.strip('-')

    return prefix


def get_default_prefix() -> str:
    """
    Get default prefix for package names.

    Auto-detects from git config. Raises error if not found.

    Returns:
        Sanitized prefix

    Raises:
        RuntimeError: If git username cannot be determined
    """
    username = get_git_username()

    if not username:
        raise RuntimeError(
            "Could not determine git username. Please either:\n"
            "  1. Configure git: git config --global github.user YOUR_USERNAME\n"
            "  2. Or provide --prefix manually: --prefix YOUR_PREFIX\n"
            "  3. Or skip prefix: --no-prefix"
        )

    prefix = sanitize_prefix(username)

    if not prefix:
        raise RuntimeError(
            f"Git username '{username}' could not be converted to valid prefix.\n"
            f"Please provide --prefix manually."
        )

    return prefix
```

### 2. Update `initialize_project()`

**Modified signature:**

```python
def initialize_project(
    package_name: str,
    author: str,
    author_email: str,
    description: str,
    url: str,
    command_name: str,
    prefix: Optional[str] = "AUTO",  # NEW: AUTO, explicit value, or None
) -> Dict[str, Any]:
    """
    Initialize a new Python project.

    Args:
        package_name: Base package name (without prefix)
        prefix: Prefix to prepend to package name.
                - "AUTO" (default): Auto-detect from git config
                - Explicit string: Use provided prefix
                - None: No prefix (skip)

    Examples:
        # Auto-detect prefix from git
        initialize_project(package_name="coolapp")
        # → "jsmith-coolapp" (if git user is jsmith)

        # Explicit prefix
        initialize_project(package_name="coolapp", prefix="myorg")
        # → "myorg-coolapp"

        # No prefix
        initialize_project(package_name="coolapp", prefix=None)
        # → "coolapp"
    """
    from vmenon25_pypi_workflow_generator.git_utils import get_default_prefix

    # Determine final prefix
    if prefix == "AUTO":
        # Auto-detect from git
        try:
            detected_prefix = get_default_prefix()
            final_package_name = f"{detected_prefix}-{package_name}"
            print(f"ℹ️  Auto-detected prefix: '{detected_prefix}'")
            print(f"ℹ️  Full package name: '{final_package_name}'")
        except RuntimeError as e:
            print(f"❌ {e}", file=sys.stderr)
            return {
                'success': False,
                'error': str(e)
            }
    elif prefix is not None:
        # Use provided prefix
        final_package_name = f"{prefix}-{package_name}"
        print(f"ℹ️  Using prefix: '{prefix}'")
        print(f"ℹ️  Full package name: '{final_package_name}'")
    else:
        # No prefix
        final_package_name = package_name
        print(f"ℹ️  No prefix (using package name as-is)")

    # Derive import name (replace hyphens with underscores)
    import_name = final_package_name.replace('-', '_')

    # Validate import name
    if not import_name.isidentifier():
        return {
            'success': False,
            'error': f"Invalid import name: {import_name}"
        }

    # Continue with existing initialization...
    # (Rest of function unchanged)

    return {
        'success': True,
        'package_name': final_package_name,
        'import_name': import_name,
        'prefix': prefix if prefix != "AUTO" else detected_prefix,
        'message': f'Created package: {import_name}/ (publishes as {final_package_name})'
    }
```

### 3. Update CLI

**Update `vmenon25_pypi_workflow_generator/cli.py`:**

```python
@click.command()
@click.option('--package-name', required=True, help='Base package name (without prefix)')
@click.option('--author', required=True, help='Author name')
@click.option('--author-email', required=True, help='Author email')
@click.option('--description', required=True, help='Package description')
@click.option('--url', required=True, help='Project URL')
@click.option('--command-name', required=True, help='CLI command name')
@click.option('--prefix', default="AUTO", help='Package name prefix (default: auto-detect from git)')
@click.option('--no-prefix', is_flag=True, help='Skip adding prefix to package name')
def init(package_name, author, author_email, description, url, command_name, prefix, no_prefix):
    """
    Initialize a new Python project with pyproject.toml and setup.py.

    By default, auto-detects your git username as a prefix to avoid PyPI naming conflicts.

    Examples:

        # Auto-detect prefix from git (default)
        pypi-workflow-generator-init --package-name coolapp --author "..." --author-email "..."

        # Use custom prefix
        pypi-workflow-generator-init --package-name coolapp --prefix myorg --author "..."

        # Skip prefix
        pypi-workflow-generator-init --package-name coolapp --no-prefix --author "..."
    """
    # Handle --no-prefix flag
    if no_prefix:
        prefix = None
    elif prefix == "AUTO":
        prefix = "AUTO"  # Will auto-detect in initialize_project

    result = initialize_project(
        package_name=package_name,
        author=author,
        author_email=author_email,
        description=description,
        url=url,
        command_name=command_name,
        prefix=prefix
    )

    if result['success']:
        click.echo(click.style('✅ ' + result['message'], fg='green'))
    else:
        click.echo(click.style('❌ ' + result['error'], fg='red'))
        sys.exit(1)
```

### 4. Update MCP Server

**Update `vmenon25_pypi_workflow_generator/server.py`:**

```python
@server.tool()
async def initialize_project(
    package_name: str,
    author: str,
    author_email: str,
    description: str,
    url: str,
    command_name: str,
    prefix: str = "AUTO"
) -> dict:
    """
    Initialize a new Python project.

    Args:
        package_name: Base package name (without prefix)
        author: Package author name
        author_email: Package author email
        description: Package description
        url: Project URL (e.g., GitHub repository)
        command_name: CLI command name for console_scripts entry point
        prefix: Package name prefix. Use "AUTO" to auto-detect from git,
                explicit string for custom prefix, or "NONE" to skip prefix.

    Returns:
        Result dict with success status and created files

    Examples:
        Auto-detect prefix:
            initialize_project(package_name="coolapp", ..., prefix="AUTO")
            → Creates "jsmith-coolapp" if git user is jsmith

        Custom prefix:
            initialize_project(package_name="coolapp", ..., prefix="myorg")
            → Creates "myorg-coolapp"

        No prefix:
            initialize_project(package_name="coolapp", ..., prefix="NONE")
            → Creates "coolapp"
    """
    # Convert "NONE" string to None
    if prefix == "NONE":
        prefix = None

    result = gen.initialize_project(
        package_name=package_name,
        author=author,
        author_email=author_email,
        description=description,
        url=url,
        command_name=command_name,
        prefix=prefix
    )

    return {
        "content": [
            {
                "type": "text",
                "text": result['message'] if result['success'] else result['error']
            }
        ],
        "isError": not result['success']
    }
```

---

## User Experience Examples

### Example 1: Auto-Detect (Happy Path)

```bash
$ git config --get github.user
jsmith

$ pypi-workflow-generator-init \
  --package-name coolapp \
  --author "John Smith" \
  --author-email "john@example.com" \
  --description "Cool application" \
  --url "https://github.com/jsmith/coolapp" \
  --command-name coolapp

ℹ️  Auto-detected prefix: 'jsmith'
ℹ️  Full package name: 'jsmith-coolapp'
✅ Created package: jsmith_coolapp/ (publishes as jsmith-coolapp)

Files created:
  - pyproject.toml
  - setup.py (name="jsmith-coolapp")
  - jsmith_coolapp/ (Python package directory)
```

### Example 2: Custom Prefix

```bash
$ pypi-workflow-generator-init \
  --package-name coolapp \
  --prefix acme \
  --author "Acme Corp" \
  --author-email "dev@acme.com" \
  --description "Cool application" \
  --url "https://github.com/acme/coolapp" \
  --command-name coolapp

ℹ️  Using prefix: 'acme'
ℹ️  Full package name: 'acme-coolapp'
✅ Created package: acme_coolapp/ (publishes as acme-coolapp)
```

### Example 3: No Prefix

```bash
$ pypi-workflow-generator-init \
  --package-name coolapp \
  --no-prefix \
  --author "..." \
  --author-email "..." \
  --description "..." \
  --url "..." \
  --command-name coolapp

ℹ️  No prefix (using package name as-is)
⚠️  Warning: Package name 'coolapp' may conflict on PyPI
💡  Consider checking availability: https://pypi.org/project/coolapp/
✅ Created package: coolapp/ (publishes as coolapp)
```

### Example 4: Git Not Configured

```bash
$ git config --get github.user
# (no output - not configured)

$ pypi-workflow-generator-init \
  --package-name coolapp \
  --author "..." \
  --author-email "..." \
  --description "..." \
  --url "..." \
  --command-name coolapp

❌ Could not determine git username. Please either:
  1. Configure git: git config --global github.user YOUR_USERNAME
  2. Or provide --prefix manually: --prefix YOUR_PREFIX
  3. Or skip prefix: --no-prefix
```

### Example 5: Name Sanitization

```bash
$ git config --get user.name
John Smith

$ pypi-workflow-generator-init --package-name coolapp ...

ℹ️  Auto-detected prefix: 'john-smith'
ℹ️  Full package name: 'john-smith-coolapp'
✅ Created package: john_smith_coolapp/ (publishes as john-smith-coolapp)
```

---

## Testing Plan

### Unit Tests

**Create `vmenon25_pypi_workflow_generator/tests/test_git_utils.py`:**

```python
"""Tests for git utility functions."""
import pytest
from unittest.mock import patch, MagicMock
from vmenon25_pypi_workflow_generator.git_utils import (
    get_git_username,
    sanitize_prefix,
    get_default_prefix
)


def test_sanitize_prefix_simple():
    """Test sanitizing simple usernames."""
    assert sanitize_prefix("jsmith") == "jsmith"
    assert sanitize_prefix("alice") == "alice"


def test_sanitize_prefix_with_spaces():
    """Test sanitizing names with spaces."""
    assert sanitize_prefix("John Smith") == "john-smith"
    assert sanitize_prefix("Alice Bob") == "alice-bob"


def test_sanitize_prefix_with_email():
    """Test sanitizing email addresses."""
    assert sanitize_prefix("jsmith@example.com") == "jsmith"
    assert sanitize_prefix("alice@company.org") == "alice"


def test_sanitize_prefix_with_special_chars():
    """Test sanitizing names with special characters."""
    assert sanitize_prefix("alice_dev") == "alice-dev"
    assert sanitize_prefix("bob's_packages") == "bobs-packages"
    assert sanitize_prefix("user#123") == "user-123"


def test_sanitize_prefix_consecutive_hyphens():
    """Test collapsing consecutive hyphens."""
    assert sanitize_prefix("alice---bob") == "alice-bob"
    assert sanitize_prefix("test--name") == "test-name"


@patch('subprocess.run')
def test_get_git_username_github_user(mock_run):
    """Test getting username from github.user."""
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="jsmith\n"
    )
    assert get_git_username() == "jsmith"


@patch('subprocess.run')
def test_get_git_username_fallback_to_user_name(mock_run):
    """Test fallback to user.name when github.user not set."""
    def side_effect(*args, **kwargs):
        cmd = args[0]
        if 'github.user' in cmd:
            return MagicMock(returncode=1, stdout="")
        elif 'user.name' in cmd:
            return MagicMock(returncode=0, stdout="John Smith\n")

    mock_run.side_effect = side_effect
    assert get_git_username() == "John Smith"


@patch('subprocess.run')
def test_get_git_username_not_configured(mock_run):
    """Test when git is not configured."""
    mock_run.return_value = MagicMock(returncode=1, stdout="")
    assert get_git_username() is None


@patch('subprocess.run')
def test_get_default_prefix_success(mock_run):
    """Test successful prefix detection."""
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="jsmith\n"
    )
    assert get_default_prefix() == "jsmith"


@patch('subprocess.run')
def test_get_default_prefix_failure(mock_run):
    """Test failure when git not configured."""
    mock_run.return_value = MagicMock(returncode=1, stdout="")

    with pytest.raises(RuntimeError, match="Could not determine git username"):
        get_default_prefix()
```

### Integration Tests

**Update `vmenon25_pypi_workflow_generator/tests/test_init.py`:**

```python
@patch('vmenon25_pypi_workflow_generator.git_utils.get_git_username')
def test_init_with_auto_prefix(mock_git, tmp_path):
    """Test initialization with auto-detected prefix."""
    mock_git.return_value = "jsmith"

    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        result = initialize_project(
            package_name="coolapp",
            author="John Smith",
            author_email="john@example.com",
            description="Cool app",
            url="https://github.com/jsmith/coolapp",
            command_name="coolapp",
            prefix="AUTO"
        )

        assert result['success']
        assert result['package_name'] == "jsmith-coolapp"
        assert result['import_name'] == "jsmith_coolapp"

        # Check directory created
        assert (tmp_path / "jsmith_coolapp").exists()

        # Check setup.py has correct name
        setup_content = (tmp_path / "setup.py").read_text()
        assert 'name="jsmith-coolapp"' in setup_content or "name='jsmith-coolapp'" in setup_content

    finally:
        os.chdir(original_cwd)


def test_init_with_custom_prefix(tmp_path):
    """Test initialization with custom prefix."""
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        result = initialize_project(
            package_name="coolapp",
            author="...",
            author_email="...",
            description="...",
            url="...",
            command_name="coolapp",
            prefix="myorg"
        )

        assert result['success']
        assert result['package_name'] == "myorg-coolapp"
        assert result['import_name'] == "myorg_coolapp"

    finally:
        os.chdir(original_cwd)


def test_init_with_no_prefix(tmp_path):
    """Test initialization without prefix."""
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        result = initialize_project(
            package_name="coolapp",
            author="...",
            author_email="...",
            description="...",
            url="...",
            command_name="coolapp",
            prefix=None
        )

        assert result['success']
        assert result['package_name'] == "coolapp"
        assert result['import_name'] == "coolapp"

    finally:
        os.chdir(original_cwd)
```

---

## Documentation Updates

### README.md

**Update Quick Start section:**

```markdown
## Quick Start

### Initialize Your Project

The generator will auto-detect your git username and use it as a prefix to avoid PyPI naming conflicts:

```bash
# Auto-detect prefix from git (recommended)
pypi-workflow-generator-init \
  --package-name coolapp \
  --author "Your Name" \
  --author-email "you@example.com" \
  --description "Cool application" \
  --url "https://github.com/username/coolapp" \
  --command-name coolapp

# Output: Creates "jsmith-coolapp" if your git username is jsmith
```

**Custom prefix for organizations:**

```bash
pypi-workflow-generator-init \
  --package-name coolapp \
  --prefix acme \
  --author "Acme Corp" \
  --author-email "dev@acme.com" \
  --description "Cool application" \
  --url "https://github.com/acme/coolapp" \
  --command-name coolapp

# Output: Creates "acme-coolapp"
```

**Skip prefix (not recommended):**

```bash
pypi-workflow-generator-init \
  --package-name coolapp \
  --no-prefix \
  --author "..." \
  # ... other options

# Output: Creates "coolapp" (may conflict on PyPI!)
```

### Why Prefixes?

PyPI has a flat namespace - only ONE package can have a given name globally. To avoid conflicts:

- ✅ **Auto-prefix** (default): Uses your git username → `jsmith-coolapp`
- ✅ **Custom prefix**: For organizations → `acme-coolapp`
- ✅ **No prefix**: Only if you're confident the name is unique

The generator auto-detects your git username from:
1. `git config --get github.user` (preferred)
2. `git config --get user.name` (fallback, sanitized)
```

**Add new section after Features:**

```markdown
## Package Naming Best Practices

### Automatic Prefix Detection

By default, the generator adds your git username as a prefix to avoid PyPI naming conflicts:

```bash
$ git config --get github.user
jsmith

$ pypi-workflow-generator-init --package-name coolapp ...
# Creates: jsmith-coolapp on PyPI
# Import: import jsmith_coolapp
```

### Configure Git Username (If Not Set)

```bash
# Set GitHub username (recommended)
git config --global github.user YOUR_GITHUB_USERNAME

# Or set git user.name (will be sanitized)
git config --global user.name "Your Name"
```

### When to Use Each Approach

**Auto-prefix (Default)** - Personal projects:
```bash
pypi-workflow-generator-init --package-name coolapp ...
# → jsmith-coolapp
```

**Custom Prefix** - Organization packages:
```bash
pypi-workflow-generator-init --package-name coolapp --prefix acme ...
# → acme-coolapp
```

**No Prefix** - Unique standalone tools:
```bash
pypi-workflow-generator-init --package-name unique-name --no-prefix ...
# → unique-name (check PyPI availability first!)
```
```

---

## Implementation Checklist

### Phase 0: Dogfooding - Rename This Project

**IMPORTANT:** Before implementing the prefix feature, rename this project to use the prefix pattern.

See detailed checklist in "Dogfooding: Renaming This Project to Use Prefix" section above.

**Summary:**
- Rename `pypi-workflow-generator` → `vmenon25-pypi-workflow-generator`
- Rename `pypi_workflow_generator/` → `vmenon25_pypi_workflow_generator/`
- Update all imports, entry points, and configuration files
- Verify builds and tests pass
- This demonstrates using `--prefix vmenon25` to override auto-detected `hitoshura25`

### Phase 1: Core Implementation

- [ ] Create `vmenon25_pypi_workflow_generator/git_utils.py`
  - [ ] Implement `get_git_username()` with GitHub remote URL detection
  - [ ] Implement `sanitize_prefix()`
  - [ ] Implement `get_default_prefix()`
  - [ ] Add comprehensive docstrings

- [ ] Update `vmenon25_pypi_workflow_generator/generator.py`
  - [ ] Add `prefix` parameter to `initialize_project()`
  - [ ] Implement prefix logic (AUTO/custom/None)
  - [ ] Update package_name and import_name generation
  - [ ] Add informational messages about prefix

- [ ] Update `vmenon25_pypi_workflow_generator/cli.py`
  - [ ] Add `--prefix` option (default="AUTO")
  - [ ] Add `--no-prefix` flag
  - [ ] Update help text with examples

- [ ] Update `vmenon25_pypi_workflow_generator/server.py`
  - [ ] Update `initialize_project` tool signature
  - [ ] Add `prefix` parameter documentation
  - [ ] Handle "NONE" string for MCP compatibility

### Phase 2: Testing

- [ ] Create `test_git_utils.py`
  - [ ] Test `sanitize_prefix()` with various inputs
  - [ ] Test `get_git_username()` with mocked subprocess
  - [ ] Test `get_default_prefix()` success and failure cases

- [ ] Update `test_init.py`
  - [ ] Test auto-prefix detection
  - [ ] Test custom prefix
  - [ ] Test no prefix
  - [ ] Test error when git not configured

- [ ] Update `test_server.py`
  - [ ] Test MCP tool with prefix options
  - [ ] Test "AUTO" and "NONE" string values

### Phase 3: Documentation

- [ ] Update README.md
  - [ ] Add Quick Start with prefix examples
  - [ ] Add "Package Naming Best Practices" section
  - [ ] Add git configuration instructions
  - [ ] Update all code examples

- [ ] Update CLI help text
  - [ ] Add examples for each prefix option
  - [ ] Explain auto-detection behavior

- [ ] Update MCP tool descriptions
  - [ ] Document prefix parameter
  - [ ] Add examples

### Phase 4: Validation

- [ ] Manual testing
  - [ ] Test with git configured
  - [ ] Test with git not configured
  - [ ] Test with various username formats
  - [ ] Test custom prefix
  - [ ] Test no prefix

- [ ] Integration testing
  - [ ] Run full workflow with auto-prefix
  - [ ] Verify package can be built
  - [ ] Verify imports work correctly

- [ ] Run all tests
  - [ ] `pytest vmenon25_pypi_workflow_generator/tests/ -v`

---

## Edge Cases and Error Handling

### 1. Git Not Installed

```python
try:
    result = subprocess.run(['git', 'config', ...])
except FileNotFoundError:
    raise RuntimeError(
        "Git not found. Please either:\n"
        "  1. Install git\n"
        "  2. Or provide --prefix manually\n"
        "  3. Or use --no-prefix"
    )
```

### 2. Git Configured with Invalid Characters

```python
username = "John@#$%Smith"
sanitized = sanitize_prefix(username)
# → "john-smith"

if not sanitized:
    raise RuntimeError("Username could not be sanitized to valid prefix")
```

### 3. Prefix Results in Invalid Import Name

```python
prefix = "123-invalid"
package_name = "coolapp"
full_name = f"{prefix}-{package_name}"  # "123-invalid-coolapp"
import_name = full_name.replace('-', '_')  # "123_invalid_coolapp"

if not import_name.isidentifier():
    raise ValueError(
        f"Prefix '{prefix}' results in invalid Python identifier.\n"
        f"Please provide a different prefix."
    )
```

### 4. User Wants Different Behavior

Provide clear flags:
- `--prefix custom`: Use specific prefix
- `--no-prefix`: Skip prefix entirely
- Default behavior: Auto-detect

---

## Benefits

### For Users

1. **Zero Configuration** - Works out of the box with git
2. **Best Practices by Default** - Encourages proper naming
3. **Flexible** - Can override or disable as needed
4. **Educational** - Users learn about PyPI naming conventions

### For PyPI Ecosystem

1. **Fewer Conflicts** - More descriptive package names
2. **Better Organization** - Related packages grouped by prefix
3. **Clearer Ownership** - Easy to identify package maintainer

---

## Migration for Existing Users

This is a **new feature** with sensible defaults, so no breaking changes:

- Existing users without `--prefix` will now get auto-prefix
- Users who want old behavior can use `--no-prefix`
- Documentation clearly explains the change

**Release Notes Text:**

```markdown
### New Feature: Automatic Package Name Prefixing

To help avoid PyPI naming conflicts, the generator now automatically adds your git username as a prefix to package names:

- **Auto-detect** (default): Uses `git config github.user` or `user.name`
- **Custom prefix**: Use `--prefix myorg` for organization packages
- **No prefix**: Use `--no-prefix` for unique standalone packages

Example:
```bash
# Before: Creates "coolapp"
pypi-workflow-generator-init --package-name coolapp ...

# Now: Creates "jsmith-coolapp" (if git user is jsmith)
pypi-workflow-generator-init --package-name coolapp ...

# To get old behavior:
pypi-workflow-generator-init --package-name coolapp --no-prefix ...
```

This follows PyPI best practices and reduces the chance of name conflicts.
```

---

## Dogfooding: Renaming This Project to Use Prefix

### Current State

This project is currently published as:
- **PyPI name:** `pypi-workflow-generator`
- **Import name:** `pypi_workflow_generator`
- **Status:** Early stage, no external users yet

### Decision: **RENAME TO USE PREFIX** ✅

Since this project has no external users yet, we will dogfood the prefix feature by renaming:

- **Old name:** `pypi-workflow-generator`
- **New name:** `vmenon25-pypi-workflow-generator`
- **Import name:** `vmenon25_pypi_workflow_generator`
- **PyPI username:** `vmenon25`

This demonstrates:
1. ✅ We use our own tooling
2. ✅ We follow our own best practices
3. ✅ Tests the `--prefix` override functionality
4. ✅ Shows prefix feature in real-world use

### Why `vmenon25` instead of `hitoshura25`?

The git remote URL shows GitHub username `hitoshura25`, but the PyPI username is `vmenon25`.

This is actually a **perfect test case** because it demonstrates:
- Auto-detection would find `hitoshura25` from git remote
- User can override with `--prefix vmenon25` to match PyPI username
- Shows that git detection is a helpful default, not a requirement

### Implementation Checklist

**Phase 0: Dogfooding - Rename Project**

- [ ] Update `pyproject.toml`
  - [ ] Change `name = "vmenon25-pypi-workflow-generator"`

- [ ] Update `setup.py`
  - [ ] Change `name = 'vmenon25-pypi-workflow-generator'`

- [ ] Rename package directory
  - [ ] `git mv pypi_workflow_generator vmenon25_pypi_workflow_generator`

- [ ] Update all imports throughout codebase
  - [ ] Replace `from pypi_workflow_generator` → `from vmenon25_pypi_workflow_generator`
  - [ ] Replace `import pypi_workflow_generator` → `import vmenon25_pypi_workflow_generator`

- [ ] Update entry points in `pyproject.toml` and `setup.py`
  - [ ] `vmenon25-pypi-workflow-generator = "vmenon25_pypi_workflow_generator.main:main"`
  - [ ] `vmenon25-pypi-workflow-generator-init = "vmenon25_pypi_workflow_generator.init:main"`
  - [ ] `vmenon25-pypi-release = "vmenon25_pypi_workflow_generator.create_release:main"`
  - [ ] `mcp-vmenon25-pypi-workflow-generator = "vmenon25_pypi_workflow_generator.server:main"`

- [ ] Update `tool.setuptools.packages.find` in `pyproject.toml`
  - [ ] Change `include = ["vmenon25_pypi_workflow_generator*"]`

- [ ] Update `tool.setuptools.package-data` in `pyproject.toml`
  - [ ] Change `vmenon25_pypi_workflow_generator = ["*.j2"]`

- [ ] Update README.md
  - [ ] Update installation instructions
  - [ ] Update all command examples
  - [ ] Update package name references

- [ ] Update test files
  - [ ] Update all import statements in tests
  - [ ] Update test fixtures if they reference package name

- [ ] Update GitHub Actions workflows
  - [ ] Update any references to package name
  - [ ] Update test commands

- [ ] Verify build and tests
  - [ ] `python -m build`
  - [ ] `pytest vmenon25_pypi_workflow_generator/tests/ -v`
  - [ ] Test CLI commands work
  - [ ] Test MCP server works

- [ ] Create migration commit
  - [ ] Clear commit message explaining the rename
  - [ ] Reference this implementation plan

- [ ] Update PyPI (when ready to publish)
  - [ ] Publish as `vmenon25-pypi-workflow-generator`
  - [ ] Consider uploading empty package to old name with deprecation notice (optional)

---

## Summary

This implementation:
1. ✅ **Auto-detects** git username from multiple sources (github.user, remote URL, user.name)
2. ✅ **Allows custom prefixes** for organizations or different PyPI usernames
3. ✅ **Can be disabled** with `--no-prefix`
4. ✅ **Fails gracefully** if git not configured
5. ✅ **Sanitizes names** to be valid Python identifiers
6. ✅ **Educates users** about PyPI naming best practices
7. ✅ **Zero breaking changes** for existing functionality
8. ✅ **Dogfooding** - This project itself uses the prefix pattern

The feature is **opinionated by default** (always adds prefix) but **flexible** (can override or disable), striking the right balance between best practices and user control.

### Dogfooding Strategy

This project practices what it preaches by:
1. **Renaming to use prefix** - `pypi-workflow-generator` → `vmenon25-pypi-workflow-generator`
2. **Demonstrates override feature** - Uses `--prefix vmenon25` despite git showing `hitoshura25`
3. **Shows real-world usage** - Not just an example, but production use
4. **Tests the full workflow** - Rename process validates the implementation

This demonstrates:
- ✅ We use our own tooling
- ✅ We follow our own best practices
- ✅ Prefix override functionality works correctly
- ✅ The feature handles real-world scenarios (git username ≠ PyPI username)

---

**END OF IMPLEMENTATION PLAN**
