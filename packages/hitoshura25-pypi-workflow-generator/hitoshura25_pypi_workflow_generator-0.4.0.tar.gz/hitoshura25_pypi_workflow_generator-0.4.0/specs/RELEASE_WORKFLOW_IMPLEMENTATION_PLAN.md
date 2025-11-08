# Release Workflow Implementation Plan
## Adding Automated Release Creation to pypi-workflow-generator

**Created**: 2025-11-01
**Status**: Ready for Implementation
**Estimated Time**: 2-3 hours

---

## Executive Summary

### What We're Building

Add a GitHub Actions workflow generator for automated release tag creation to the `pypi-workflow-generator` tool. This will enable users to create releases via GitHub UI instead of running CLI commands locally.

### Why This Matters

**Current Problem**:
- Creating releases requires local CLI usage (`pypi-release minor`)
- Token-intensive when done via AI (research, planning, git operations)
- Manual process that could be automated

**Solution**:
- Generate a `create-release.yml` workflow alongside `pypi-publish.yml`
- Users trigger releases from GitHub Actions UI (0 tokens)
- Fully automated version calculation and tag creation
- Auto-generated release notes from commits

### User Requirements (from Q&A)

1. **GitHub Releases**: Include with auto-generated notes (using built-in GitHub feature)
2. **Default Trigger**: Manual only via `workflow_dispatch`
3. **CLI Interface**: Separate command (`pypi-workflow-generator-release`)
4. **Default Behavior**: Generate BOTH workflows by default (opt-out model)

---

## Architecture Decisions

### Decision 1: Separate Workflow File ✅

**Chosen Approach**: Create `create-release.yml` separate from `pypi-publish.yml`

**Rationale**:
- Clear separation of concerns (tag creation vs package publishing)
- Each workflow has focused permissions
- Easier to debug and maintain
- Follows single responsibility principle
- Natural trigger chain: manual UI → create tag → tag push → publish

**Alternative Considered**: Combined workflow with conditionals ❌
- Rejected: Too complex, mixed concerns, harder to maintain

### Decision 2: Default Behavior

**Chosen Approach**: Generate BOTH workflows by default

**Implementation**:
```python
# In generate_workflow()
def generate_workflow(..., include_release_workflow=True):
    # Generate pypi-publish.yml
    ...

    # Also generate create-release.yml by default
    if include_release_workflow:
        generate_release_workflow(...)
```

**Rationale**:
- Complete automation out-of-the-box
- Users expect both workflows together
- Can opt-out with `--skip-release-workflow` flag
- Dogfooding: our own project will use both

### Decision 3: CLI Interface

**Chosen Approach**: Separate command + convenience flag

**Commands**:
```bash
# Generate both workflows (default)
pypi-workflow-generator --python-version 3.11

# Generate only publish workflow
pypi-workflow-generator --skip-release-workflow

# Generate only release workflow
pypi-workflow-generator-release
```

**Entry Points** (in setup.py):
```python
entry_points={
    'console_scripts': [
        'pypi-workflow-generator=pypi_workflow_generator.main:main',
        'pypi-workflow-generator-init=pypi_workflow_generator.init:main',
        'pypi-release=pypi_workflow_generator.create_release:main',
        'pypi-workflow-generator-release=pypi_workflow_generator.release_workflow:main',  # NEW
        'mcp-pypi-workflow-generator=pypi_workflow_generator.server:main',
    ],
}
```

### Decision 4: GitHub Releases

**Chosen Approach**: Include GitHub Releases with auto-generated notes

**Implementation** (in workflow):
```yaml
- name: Create GitHub Release
  run: |
    gh release create ${{ steps.calc_version.outputs.new_version }} \
      --title "Release ${{ steps.calc_version.outputs.new_version }}" \
      --generate-notes  # Auto-generates from commits!
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**How it works**:
- GitHub CLI (`gh`) is pre-installed in Actions runners
- `--generate-notes` automatically creates release notes from commits since last release
- Groups commits by category (Features, Bug Fixes, Other Changes)
- Free, built-in, no complexity

**Example Output**:
```
## What's Changed
* Add exit code handling by @user in #123
* Fix pytest-asyncio dependency by @user in #124
* Update test assertions to be more Pythonic by @user in #125

**Full Changelog**: https://github.com/user/repo/compare/v0.1.0...v0.2.0
```

---

## Detailed Implementation Steps

### Step 1: Create Template File

**File**: `pypi_workflow_generator/create_release.yml.j2`

**Full Template** (65 lines):

```yaml
name: Create Release

# Manual trigger for creating release tags
on:
  workflow_dispatch:
    inputs:
      release_type:
        description: 'Type of version bump'
        required: true
        type: choice
        options:
          - patch
          - minor
          - major

jobs:
  create-release:
    runs-on: ubuntu-latest
    permissions:
      contents: write  # Required for creating tags and releases

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Need full history for tags
          fetch-tags: true

      - name: Get latest tag
        id: get_latest_tag
        run: |
          latest_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
          echo "latest_tag=$latest_tag" >> $GITHUB_OUTPUT
          echo "Latest tag: $latest_tag"

      - name: Calculate new version
        id: calc_version
        run: |
          latest_tag="${{ steps.get_latest_tag.outputs.latest_tag }}"
          version=${latest_tag#v}
          IFS='.' read -r major minor patch <<< "$version"

          release_type="${{ github.event.inputs.release_type }}"

          case $release_type in
            major)
              major=$((major + 1))
              minor=0
              patch=0
              ;;
            minor)
              minor=$((minor + 1))
              patch=0
              ;;
            patch)
              patch=$((patch + 1))
              ;;
          esac

          new_version="v${major}.${minor}.${patch}"
          echo "new_version=$new_version" >> $GITHUB_OUTPUT
          echo "New version: $new_version"

      - name: Create and push tag
        run: |
          new_version="${{ steps.calc_version.outputs.new_version }}"
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git tag -a "$new_version" -m "Release $new_version"
          git push origin "$new_version"
          echo "✅ Created and pushed tag: $new_version"

      - name: Create GitHub Release
        run: |
          gh release create ${{ steps.calc_version.outputs.new_version }} \
            --title "Release ${{ steps.calc_version.outputs.new_version }}" \
            --generate-notes
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Summary
        run: |
          echo "### Release Created :rocket:" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**Version**: ${{ steps.calc_version.outputs.new_version }}" >> $GITHUB_STEP_SUMMARY
          echo "**Type**: ${{ github.event.inputs.release_type }}" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "The tag has been pushed and will trigger the PyPI publish workflow." >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "[View Release](https://github.com/${{ github.repository }}/releases/tag/${{ steps.calc_version.outputs.new_version }})" >> $GITHUB_STEP_SUMMARY
```

**Template Variables**: None needed for Phase 1 (all hardcoded for simplicity)

**Future Enhancement**: Could add Jinja2 variables for:
- `create_github_release` (boolean) - make releases optional
- `auto_release_on_main` (boolean) - auto-create patch on main push
- But keeping it simple for now

---

### Step 2: Update generator.py

**File**: `pypi_workflow_generator/generator.py`

**Add New Function** (after existing `generate_workflow` function):

```python
def generate_release_workflow(
    output_filename: str = 'create-release.yml',
    base_output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate GitHub Actions workflow for automated release creation.

    This workflow allows users to create releases via GitHub Actions UI,
    automating version calculation, tag creation, and GitHub Release generation.

    Args:
        output_filename: Name of generated workflow file (default: 'create-release.yml')
        base_output_dir: Custom output directory (default: .github/workflows)

    Returns:
        Dict with:
            - success (bool): Whether generation succeeded
            - file_path (str): Full path to generated file
            - message (str): Status message

    Example:
        >>> result = generate_release_workflow()
        >>> print(result['message'])
        Successfully generated .github/workflows/create-release.yml
    """
    # Get template directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(script_dir))
    template = env.get_template('create_release.yml.j2')

    # Render template (no variables needed for Phase 1)
    workflow_content = template.render()

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
```

**Modify Existing Function** (add parameter):

```python
def generate_workflow(
    python_version: str = '3.11',
    output_filename: str = 'pypi-publish.yml',
    release_on_main_push: bool = False,
    test_path: str = '.',
    base_output_dir: Optional[str] = None,
    verbose_publish: bool = False,
    include_release_workflow: bool = True  # NEW PARAMETER
) -> Dict[str, Any]:
    """
    Generate GitHub Actions workflow for PyPI publishing.

    ... existing docstring ...

    Args:
        ... existing args ...
        include_release_workflow: Also generate create-release.yml workflow (default: True)

    Returns:
        Dict with success status and file paths (may include multiple files)
    """
    # Existing workflow generation code...

    result = {
        'success': True,
        'file_path': full_output_path,
        'message': f"Successfully generated {full_output_path}",
        'files_created': [full_output_path]  # NEW: track all files
    }

    # NEW: Also generate release workflow by default
    if include_release_workflow:
        release_result = generate_release_workflow(
            base_output_dir=base_output_dir
        )
        if release_result['success']:
            result['files_created'].append(release_result['file_path'])
            result['message'] += f"\nSuccessfully generated {release_result['file_path']}"

    return result
```

**Update __all__** (if present):

```python
__all__ = [
    'generate_workflow',
    'initialize_project',
    'create_git_release',
    'generate_release_workflow',  # NEW
]
```

---

### Step 3: Create New CLI Entry Point

**File**: `pypi_workflow_generator/release_workflow.py` (NEW)

```python
#!/usr/bin/env python3
"""
CLI for generating GitHub Actions release workflow.

This generates a workflow that allows users to create releases via
GitHub Actions UI, with automatic version calculation and tag creation.
"""

import argparse
import sys
from .generator import generate_release_workflow


def main():
    """Main CLI entry point for release workflow generation."""
    parser = argparse.ArgumentParser(
        description='Generate a GitHub Actions workflow for creating releases.',
        epilog="""
Examples:
  # Generate create-release.yml in .github/workflows/
  pypi-workflow-generator-release

  # Custom filename
  pypi-workflow-generator-release --output-filename my-release.yml
        """
    )

    parser.add_argument(
        '--output-filename',
        default='create-release.yml',
        help='Name for the generated workflow file (default: create-release.yml)'
    )

    args = parser.parse_args()

    try:
        result = generate_release_workflow(
            output_filename=args.output_filename
        )
        print(result['message'])
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

---

### Step 4: Update MCP Server

**File**: `pypi_workflow_generator/server.py`

**Update Import**:

```python
from .generator import (
    generate_workflow,
    initialize_project,
    create_git_release,
    generate_release_workflow  # NEW
)
```

**Add Tool in `handle_list_tools()`** (after existing tools):

```python
{
    "name": "generate_release_workflow",
    "description": "Generate GitHub Actions workflow for creating releases via UI. Allows manual release creation with automatic version calculation and tag creation.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "output_filename": {
                "type": "string",
                "description": "Name of the workflow file",
                "default": "create-release.yml"
            }
        },
        "required": []
    }
}
```

**Add Handler in `handle_call_tool()`** (in the elif chain):

```python
elif tool_name == "generate_release_workflow":
    result = generate_release_workflow(**arguments)
    return {
        "content": [
            {
                "type": "text",
                "text": result['message']
            }
        ],
        "isError": not result['success']
    }
```

**Update `generate_workflow` Tool Schema** (add new parameter):

```python
{
    "name": "generate_workflow",
    "description": "Generate GitHub Actions workflow for automated PyPI publishing",
    "inputSchema": {
        "type": "object",
        "properties": {
            # ... existing properties ...
            "include_release_workflow": {
                "type": "boolean",
                "description": "Also generate create-release.yml workflow for manual releases",
                "default": True
            }
        },
        "required": []
    }
}
```

---

### Step 5: Update main.py CLI

**File**: `pypi_workflow_generator/main.py`

**Add Argument**:

```python
parser.add_argument(
    '--skip-release-workflow',
    action='store_true',
    help='Do not generate the create-release.yml workflow (only generate pypi-publish.yml)'
)
```

**Update Function Call**:

```python
result = generate_workflow(
    python_version=args.python_version,
    output_filename=args.output_filename,
    release_on_main_push=args.release_on_main_push,
    test_path=args.test_path,
    verbose_publish=args.verbose_publish,
    include_release_workflow=not args.skip_release_workflow  # NEW
)
```

**Update Output Message**:

```python
print(result['message'])  # Now includes both files if generated
return 0
```

---

### Step 6: Update setup.py

**File**: `setup.py`

**Add Entry Point**:

```python
entry_points={
    'console_scripts': [
        'pypi-workflow-generator=pypi_workflow_generator.main:main',
        'pypi-workflow-generator-init=pypi_workflow_generator.init:main',
        'pypi-release=pypi_workflow_generator.create_release:main',
        'pypi-workflow-generator-release=pypi_workflow_generator.release_workflow:main',  # NEW
        'mcp-pypi-workflow-generator=pypi_workflow_generator.server:main',
    ],
},
```

No other changes needed - `MANIFEST.in` already includes `*.j2` files.

---

### Step 7: Add Tests

**File**: `pypi_workflow_generator/tests/test_release_workflow.py` (NEW)

```python
"""
Tests for release workflow generation.
"""
import os
import pytest
from pypi_workflow_generator.generator import generate_release_workflow


def test_generate_release_workflow_default(tmp_path):
    """Test release workflow generation with default arguments."""
    output_dir = tmp_path / ".github" / "workflows"
    result = generate_release_workflow(
        base_output_dir=output_dir
    )

    assert result['success']
    assert 'file_path' in result
    assert 'message' in result

    output_file = output_dir / 'create-release.yml'
    assert output_file.exists()

    with open(output_file, 'r') as f:
        content = f.read()

    # Verify workflow structure
    assert "name: Create Release" in content
    assert "workflow_dispatch" in content
    assert "release_type" in content
    assert "patch" in content
    assert "minor" in content
    assert "major" in content
    assert "Create GitHub Release" in content
    assert "generate-notes" in content


def test_generate_release_workflow_custom_filename(tmp_path):
    """Test release workflow with custom filename."""
    output_dir = tmp_path / ".github" / "workflows"
    result = generate_release_workflow(
        output_filename='my-release.yml',
        base_output_dir=output_dir
    )

    assert result['success']

    output_file = output_dir / 'my-release.yml'
    assert output_file.exists()

    with open(output_file, 'r') as f:
        content = f.read()

    assert "workflow_dispatch" in content


def test_generate_release_workflow_creates_directory(tmp_path):
    """Test that workflow generation creates output directory if needed."""
    output_dir = tmp_path / ".github" / "workflows"
    assert not output_dir.exists()

    result = generate_release_workflow(
        base_output_dir=output_dir
    )

    assert result['success']
    assert output_dir.exists()
    assert (output_dir / 'create-release.yml').exists()


def test_generate_workflow_includes_release_by_default(tmp_path):
    """Test that generate_workflow creates both workflows by default."""
    from pypi_workflow_generator.generator import generate_workflow

    output_dir = tmp_path / ".github" / "workflows"
    result = generate_workflow(
        python_version='3.11',
        base_output_dir=output_dir
    )

    assert result['success']
    assert 'files_created' in result
    assert len(result['files_created']) == 2

    # Both workflows should exist
    assert (output_dir / 'pypi-publish.yml').exists()
    assert (output_dir / 'create-release.yml').exists()


def test_generate_workflow_skip_release(tmp_path):
    """Test that generate_workflow can skip release workflow."""
    from pypi_workflow_generator.generator import generate_workflow

    output_dir = tmp_path / ".github" / "workflows"
    result = generate_workflow(
        python_version='3.11',
        base_output_dir=output_dir,
        include_release_workflow=False
    )

    assert result['success']
    assert len(result['files_created']) == 1

    # Only publish workflow should exist
    assert (output_dir / 'pypi-publish.yml').exists()
    assert not (output_dir / 'create-release.yml').exists()
```

**File**: `pypi_workflow_generator/tests/test_server.py` (MODIFY)

**Update Tool Count Assertion**:

```python
def test_list_tools():
    """Test that list_tools returns correct structure."""
    server = MCPServer()
    result = server.handle_list_tools()

    assert "tools" in result
    assert len(result["tools"]) == 4  # Changed from 3

    # Verify tool names
    tool_names = [tool["name"] for tool in result["tools"]]
    assert "generate_workflow" in tool_names
    assert "initialize_project" in tool_names
    assert "create_release" in tool_names
    assert "generate_release_workflow" in tool_names  # NEW
```

**Add New MCP Tests**:

```python
@pytest.mark.asyncio
async def test_call_tool_generate_release_workflow(tmp_path):
    """Test calling generate_release_workflow tool via MCP."""
    server = MCPServer()

    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        result = await server.handle_call_tool(
            "generate_release_workflow",
            {}
        )

        assert "content" in result
        assert result.get("isError") == False
        assert "Successfully generated" in result["content"][0]["text"]

        workflow_path = tmp_path / ".github" / "workflows" / "create-release.yml"
        assert workflow_path.exists()

        content = workflow_path.read_text()
        assert "workflow_dispatch" in content
        assert "Create GitHub Release" in content

    finally:
        os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_call_tool_generate_release_workflow_custom_filename(tmp_path):
    """Test release workflow with custom filename via MCP."""
    server = MCPServer()

    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        result = await server.handle_call_tool(
            "generate_release_workflow",
            {"output_filename": "custom-release.yml"}
        )

        assert result.get("isError") == False

        workflow_path = tmp_path / ".github" / "workflows" / "custom-release.yml"
        assert workflow_path.exists()

    finally:
        os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_generate_workflow_includes_release_via_mcp(tmp_path):
    """Test that generate_workflow MCP tool creates both workflows by default."""
    server = MCPServer()

    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        result = await server.handle_call_tool(
            "generate_workflow",
            {"python_version": "3.11"}
        )

        assert result.get("isError") == False

        # Both workflows should exist
        assert (tmp_path / ".github" / "workflows" / "pypi-publish.yml").exists()
        assert (tmp_path / ".github" / "workflows" / "create-release.yml").exists()

    finally:
        os.chdir(original_cwd)
```

**Test Count Update**:
- Before: 15 tests (11 server + 2 generator + 1 init + 1 release)
- After: 23 tests (14 server + 4 generator + 1 init + 1 release + 3 release_workflow)

---

## File Changes Summary

### New Files (3)

1. **pypi_workflow_generator/create_release.yml.j2**
   - Lines: ~65
   - Type: Jinja2 template
   - Purpose: GitHub Actions workflow template

2. **pypi_workflow_generator/release_workflow.py**
   - Lines: ~45
   - Type: Python CLI
   - Purpose: Standalone command for release workflow generation

3. **pypi_workflow_generator/tests/test_release_workflow.py**
   - Lines: ~120
   - Type: Python tests
   - Purpose: Test release workflow generation

### Modified Files (5)

1. **pypi_workflow_generator/generator.py**
   - Add: `generate_release_workflow()` function (~40 lines)
   - Modify: `generate_workflow()` function (add parameter + logic, ~10 lines)
   - Total changes: ~50 lines

2. **pypi_workflow_generator/server.py**
   - Add: Import for `generate_release_workflow`
   - Add: Tool definition in `handle_list_tools()` (~15 lines)
   - Add: Handler in `handle_call_tool()` (~8 lines)
   - Modify: `generate_workflow` tool schema (add parameter)
   - Total changes: ~25 lines

3. **pypi_workflow_generator/main.py**
   - Add: `--skip-release-workflow` argument (~4 lines)
   - Modify: Function call (add parameter, ~1 line)
   - Modify: Output message (~1 line)
   - Total changes: ~6 lines

4. **pypi_workflow_generator/tests/test_server.py**
   - Modify: Tool count assertion (~1 line)
   - Add: 3 new test functions (~60 lines)
   - Total changes: ~61 lines

5. **setup.py**
   - Add: Entry point for `pypi-workflow-generator-release` (~1 line)
   - Total changes: ~1 line

### Total Implementation Size

- **New code**: ~230 lines
- **Modified code**: ~143 lines
- **Template**: ~65 lines
- **Tests**: ~180 lines
- **Grand total**: ~618 lines

---

## Testing Strategy

### Phase 1: Unit Tests

Run individual tests:

```bash
# Test release workflow generation
pytest pypi_workflow_generator/tests/test_release_workflow.py -v

# Test MCP integration
pytest pypi_workflow_generator/tests/test_server.py::test_call_tool_generate_release_workflow -v

# Test default behavior
pytest pypi_workflow_generator/tests/test_release_workflow.py::test_generate_workflow_includes_release_by_default -v
```

Expected: All 8 new tests pass (5 in test_release_workflow.py + 3 in test_server.py)

### Phase 2: Integration Tests

Test full workflow:

```bash
# Test CLI
pypi-workflow-generator-release
ls .github/workflows/create-release.yml  # Should exist

# Test main CLI generates both
rm -rf .github/workflows/
pypi-workflow-generator --python-version 3.11
ls .github/workflows/  # Should see both files

# Test skip flag
rm -rf .github/workflows/
pypi-workflow-generator --skip-release-workflow
ls .github/workflows/  # Should see only pypi-publish.yml
```

### Phase 3: MCP Protocol Tests

Test via MCP server:

```bash
# Start server
mcp-pypi-workflow-generator

# Send list_tools request
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | mcp-pypi-workflow-generator

# Expected: 4 tools including generate_release_workflow

# Send generate_release_workflow request
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"generate_release_workflow","arguments":{}}}' | mcp-pypi-workflow-generator

# Verify file created
ls .github/workflows/create-release.yml
```

### Phase 4: Full Test Suite

```bash
# Run all tests
pytest pypi_workflow_generator/tests/ -v

# Expected results:
# - 23 tests total (up from 15)
# - All passing
# - Coverage for new functionality
```

---

## Dogfooding Plan

### Step 1: Regenerate Workflows for This Project

```bash
cd /Users/vinayakmenon/pypi-workflow-generator

# Backup existing workflow (just in case)
cp .github/workflows/pypi-publish.yml .github/workflows/pypi-publish.yml.backup

# Regenerate both workflows using the new code
pypi-workflow-generator \
  --python-version 3.11 \
  --test-path pypi_workflow_generator/ \
  --verbose-publish

# Verify both files were created
ls -la .github/workflows/

# Expected output:
# pypi-publish.yml
# create-release.yml
```

### Step 2: Update Workflow Headers

Add dogfooding comments to both workflows:

**In pypi-publish.yml**:
```yaml
# This workflow was generated by pypi-workflow-generator (dogfooding!)
# Command: pypi-workflow-generator --python-version 3.11 --test-path pypi_workflow_generator/ --verbose-publish
```

**In create-release.yml**:
```yaml
# This workflow was generated by pypi-workflow-generator (dogfooding!)
# Command: pypi-workflow-generator --python-version 3.11 --test-path pypi_workflow_generator/ --verbose-publish
# Note: Both workflows are generated together by default
```

### Step 3: Commit and Push

```bash
git add .github/workflows/create-release.yml
git add pypi_workflow_generator/
git add pypi_workflow_generator/tests/
git add setup.py
git add RELEASE_WORKFLOW_IMPLEMENTATION_PLAN.md

git commit -m "Add release workflow generation

- New generate_release_workflow() function
- New pypi-workflow-generator-release CLI command
- New MCP tool: generate_release_workflow
- Default: generate both workflows together
- Add --skip-release-workflow flag
- Includes GitHub Releases with auto-generated notes
- 8 new tests (23 total, was 15)
- Dogfooding: generates both workflows for this project"

git push origin main
```

### Step 4: Test Release Workflow in GitHub Actions

1. **Navigate to GitHub Actions tab**
   - URL: https://github.com/hitoshura25/pypi-workflow-generator/actions

2. **Select "Create Release" workflow**
   - Should see new workflow in left sidebar

3. **Click "Run workflow" button**
   - Dropdown should appear with:
     - Branch: main (default)
     - Release type: patch/minor/major

4. **Select "patch" and click "Run workflow"**

5. **Monitor execution**
   - Watch workflow run in real-time
   - Verify each step completes successfully
   - Check step summary for release link

6. **Verify tag creation**
   - Go to repository tags
   - Should see new tag (e.g., v0.2.1)

7. **Verify GitHub Release**
   - Go to Releases page
   - Should see new release with auto-generated notes
   - Notes should include commits since v0.2.0

8. **Verify pypi-publish.yml triggered**
   - Check Actions tab
   - Should see pypi-publish.yml workflow running
   - Triggered by the tag push
   - Should publish new version to PyPI

### Step 5: Verify End-to-End Flow

**Expected flow**:
1. ✅ Manual trigger from UI
2. ✅ create-release.yml calculates version (v0.2.0 → v0.2.1)
3. ✅ Creates git tag
4. ✅ Pushes tag to GitHub
5. ✅ Creates GitHub Release with auto-generated notes
6. ✅ Tag push triggers pypi-publish.yml
7. ✅ Tests run
8. ✅ Package builds
9. ✅ Publishes to PyPI
10. ✅ New version v0.2.1 available on PyPI

### Step 6: Test Error Cases

1. **Test duplicate tag handling**
   - Try to create same version again
   - Should fail gracefully (tag already exists)

2. **Test from feature branch**
   - Switch to feature branch
   - Try to trigger workflow
   - Should work (creates tag from that branch)

3. **Test major/minor bumps**
   - Create minor release: v0.2.1 → v0.3.0
   - Create major release: v0.3.0 → v1.0.0
   - Verify version calculations correct

---

## Documentation Updates

### Update README.md

Add new section after "Usage" section:

```markdown
## Creating Releases

This tool now generates TWO GitHub Actions workflows by default:

### 1. PyPI Publishing Workflow (`pypi-publish.yml`)
- Automated testing on pull requests
- TestPyPI publishing on PRs
- PyPI publishing on version tags
- Uses Trusted Publishers (no API tokens needed)

### 2. Release Creation Workflow (`create-release.yml`)
- **NEW!** Manual release creation via GitHub UI
- Automatic version calculation (major/minor/patch)
- Creates git tags and pushes to GitHub
- Auto-generates release notes from commits
- Triggers the PyPI publishing workflow automatically

### Creating a Release from GitHub UI

1. Go to **Actions** tab in your repository
2. Select **Create Release** workflow
3. Click **Run workflow**
4. Choose release type:
   - **patch**: Bug fixes (0.1.0 → 0.1.1)
   - **minor**: New features (0.1.1 → 0.2.0)
   - **major**: Breaking changes (0.2.0 → 1.0.0)
5. Click **Run workflow**

The workflow will:
- Calculate the next version number
- Create and push a git tag
- Create a GitHub Release with auto-generated notes
- Automatically trigger the PyPI publish workflow
- Publish your package to PyPI

### Creating a Release from CLI (Alternative)

You can still use the CLI for local tag creation:

```bash
pypi-release patch  # or minor, major
```

This creates and pushes the tag locally, which triggers the publish workflow.

### Generating Workflows

```bash
# Generate both workflows (default)
pypi-workflow-generator --python-version 3.11

# Generate only PyPI publishing workflow
pypi-workflow-generator --skip-release-workflow

# Generate only release creation workflow
pypi-workflow-generator-release
```

## Dogfooding

This project uses itself to generate BOTH of its workflows! The workflow files at:
- `.github/workflows/pypi-publish.yml`
- `.github/workflows/create-release.yml`

Were created by running:
```bash
pypi-workflow-generator \
  --python-version 3.11 \
  --test-path pypi_workflow_generator/ \
  --verbose-publish
```

This validates that the tool works correctly and follows its own best practices.
```

### Update MCP-USAGE.md

Add new tool to the "Available Tools" section:

```markdown
### 4. generate_release_workflow

Generate a GitHub Actions workflow for creating releases via UI.

**Parameters**:
- `output_filename` (string, optional): Workflow filename, default "create-release.yml"

**What it does**:
- Creates a workflow for manual release creation
- Includes automatic version calculation (major/minor/patch)
- Creates git tags and GitHub releases
- Auto-generates release notes from commits

**Example**:
```json
{
  "name": "generate_release_workflow",
  "arguments": {}
}
```

**Generated workflow features**:
- Manual trigger via `workflow_dispatch`
- Choice input for release type (patch/minor/major)
- Automatic version calculation from latest git tag
- Creates and pushes git tags
- Creates GitHub Releases with auto-generated notes
- Triggers PyPI publish workflow automatically

**Use case**: Enable users to create releases by clicking a button in GitHub UI instead of running CLI commands locally.
```

Update the "Example Workflow" section:

```markdown
## Example Workflow: Setting Up a New Project

1. **Initialize project structure**
   ```json
   {
     "name": "initialize_project",
     "arguments": {
       "package_name": "my-awesome-tool",
       "author": "Your Name",
       "author_email": "you@example.com",
       "description": "My awesome Python package",
       "url": "https://github.com/you/my-awesome-tool",
       "command_name": "my-awesome-tool"
     }
   }
   ```

2. **Generate workflows** (both PyPI publishing and release creation)
   ```json
   {
     "name": "generate_workflow",
     "arguments": {
       "python_version": "3.11",
       "test_path": "my_awesome_tool",
       "verbose_publish": true
     }
   }
   ```

   This creates:
   - `.github/workflows/pypi-publish.yml` (for publishing)
   - `.github/workflows/create-release.yml` (for releases)

3. **Later: Create a release via UI**
   - Go to GitHub Actions tab
   - Select "Create Release" workflow
   - Run with release type: patch/minor/major
   - Package automatically publishes to PyPI
```

---

## Future Enhancements (Post-MVP)

### Phase 2: Template Variables

Add Jinja2 variables for customization:

```python
def generate_release_workflow(
    auto_release_on_main: bool = False,  # NEW
    default_release_type: str = 'patch',  # NEW
    create_github_release: bool = True,   # NEW
    ...
):
```

**Use cases**:
- `auto_release_on_main=True`: Auto-create patch releases on main branch pushes
- `create_github_release=False`: Only create tags, skip GitHub Releases
- `default_release_type='minor'`: Default to minor bumps for auto-releases

### Phase 3: Changelog Generation

Integrate with conventional commits:

- Parse commit messages for type (feat/fix/docs/etc.)
- Generate structured changelog
- Update CHANGELOG.md file automatically
- Include in GitHub Release notes

**Tools to consider**:
- `conventional-changelog`
- `git-cliff`
- GitHub's Release Please

### Phase 4: Pre-release Support

Add support for pre-releases:

- alpha: v1.0.0-alpha.1
- beta: v1.0.0-beta.1
- rc: v1.0.0-rc.1

**Implementation**:
- Add `pre_release` choice to workflow inputs
- Update version calculation logic
- Mark as pre-release in GitHub

### Phase 5: Custom Version Schemes

Support different versioning schemes:

- CalVer: 2025.11.1
- SemVer with build metadata: 1.0.0+build.123
- Custom patterns: v1.0.0-prod

---

## Success Criteria

### Must Have (MVP)

- ✅ Generate `create-release.yml` workflow template
- ✅ Manual trigger via workflow_dispatch
- ✅ Automatic version calculation (major/minor/patch)
- ✅ Create and push git tags
- ✅ Create GitHub Releases with auto-generated notes
- ✅ Both workflows generated by default
- ✅ New CLI command: `pypi-workflow-generator-release`
- ✅ New MCP tool: `generate_release_workflow`
- ✅ Skip flag: `--skip-release-workflow`
- ✅ Comprehensive tests (8+ new tests)
- ✅ Dogfooding on this project
- ✅ Updated documentation

### Should Have

- ✅ Clear error messages
- ✅ Step summaries in GitHub Actions
- ✅ Template comments explaining workflow
- ✅ Example usage in docs

### Nice to Have (Future)

- ⏳ Template variables for customization
- ⏳ Auto-release on main push option
- ⏳ Conventional commit changelog
- ⏳ Pre-release support

---

## Timeline and Estimates

### Development Phase (2-3 hours)

1. **Create template** (30 min)
   - Write create_release.yml.j2
   - Test YAML syntax

2. **Update generator.py** (30 min)
   - Add generate_release_workflow() function
   - Modify generate_workflow() function
   - Test locally

3. **Create CLI** (15 min)
   - Write release_workflow.py
   - Update setup.py
   - Test entry point

4. **Update MCP server** (20 min)
   - Add tool definition
   - Add handler
   - Update schema
   - Test protocol

5. **Update main CLI** (10 min)
   - Add --skip-release-workflow flag
   - Update function call

6. **Write tests** (45 min)
   - test_release_workflow.py (5 tests)
   - Update test_server.py (3 tests)
   - Run full test suite

7. **Update documentation** (20 min)
   - README.md
   - MCP-USAGE.md
   - This plan document

### Testing Phase (30 min)

1. **Unit tests** (10 min)
2. **Integration tests** (10 min)
3. **MCP protocol tests** (10 min)

### Dogfooding Phase (30 min)

1. **Regenerate workflows** (5 min)
2. **Commit and push** (5 min)
3. **Test in GitHub Actions** (15 min)
4. **Verify end-to-end flow** (5 min)

**Total Estimated Time**: 3 hours

---

## Risk Assessment

### Low Risk

- ✅ Template creation - straightforward YAML
- ✅ Function addition - follows existing pattern
- ✅ CLI creation - copy of existing structure
- ✅ Tests - similar to existing tests

### Medium Risk

- ⚠️ MCP protocol changes - need to ensure backward compatibility
  - **Mitigation**: Adding tool doesn't break existing clients
- ⚠️ Default behavior change - generates 2 files instead of 1
  - **Mitigation**: Opt-out flag available, clear documentation

### Negligible Risk

- GitHub Actions workflow - tested syntax
- Auto-generated notes - built-in GitHub feature
- Version calculation - simple bash arithmetic

---

## Dependencies

### Required (Already Installed)

- Python 3.11+
- Jinja2 (for templates)
- pytest (for tests)
- pytest-asyncio (for async tests)

### No New Dependencies

All features use:
- GitHub Actions built-in features
- GitHub CLI (pre-installed in runners)
- Standard bash commands
- Existing Python libraries

---

## Rollback Plan

If issues arise after deployment:

### Option 1: Quick Fix

- Users can skip release workflow: `--skip-release-workflow`
- MCP clients can avoid calling `generate_release_workflow`
- Existing functionality unchanged

### Option 2: Partial Rollback

- Remove default generation (set `include_release_workflow=False` by default)
- Keep the tool available for opt-in usage

### Option 3: Full Rollback

- Revert commits
- Remove template file
- Remove CLI entry point
- Update tests
- Publish patch release

**Rollback is low-risk** because:
- Additive changes only (no breaking changes)
- Existing tools unaffected
- Default can be toggled with 1-line change

---

## Questions & Answers

### Q: Why generate both workflows by default?

**A**: Most users want complete automation. Generating both provides a better out-of-box experience. Users who only want one can use `--skip-release-workflow`.

### Q: Why separate workflow files?

**A**: Separation of concerns. Each workflow has a focused purpose, different permissions, and different triggers. Easier to maintain and debug.

### Q: Why not use pypi-release command in the workflow?

**A**: Installing the package in the workflow adds complexity and circular dependencies. Pure bash is simpler, faster, and more reliable.

### Q: What about auto-release on every main push?

**A**: Phase 2 feature. Manual-only for MVP keeps things simple and predictable. Can add auto-release as opt-in later.

### Q: How are release notes generated?

**A**: GitHub's built-in feature (`gh release create --generate-notes`). It automatically groups commits by type and generates a professional changelog. No additional tools needed.

### Q: Can users customize the workflow?

**A**: Yes! Generated files can be edited. For common customizations, we can add template variables in Phase 2.

### Q: What if a tag already exists?

**A**: Workflow will fail with clear error message. User can delete the tag manually or use force flag (future enhancement).

---

## Implementation Checklist

### Pre-Implementation

- [x] Research completed
- [x] Design decisions documented
- [x] User requirements clarified
- [x] Implementation plan written

### Implementation

- [ ] Create `create_release.yml.j2` template
- [ ] Add `generate_release_workflow()` to generator.py
- [ ] Modify `generate_workflow()` to call it by default
- [ ] Create `release_workflow.py` CLI
- [ ] Update `main.py` with --skip-release-workflow flag
- [ ] Update `server.py` MCP tool
- [ ] Update `setup.py` entry points
- [ ] Write tests in `test_release_workflow.py`
- [ ] Update tests in `test_server.py`
- [ ] Run full test suite
- [ ] Update README.md
- [ ] Update MCP-USAGE.md

### Testing

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] MCP protocol tests pass
- [ ] Full test suite passes (23 tests)
- [ ] CLI commands work
- [ ] MCP tools work

### Dogfooding

- [ ] Regenerate both workflows for this project
- [ ] Update workflow headers with dogfooding comments
- [ ] Commit and push to GitHub
- [ ] Trigger create-release workflow manually
- [ ] Verify tag creation
- [ ] Verify GitHub Release creation
- [ ] Verify PyPI publish triggered
- [ ] Verify end-to-end flow works

### Documentation

- [ ] README.md updated
- [ ] MCP-USAGE.md updated
- [ ] Implementation plan complete
- [ ] Code comments clear
- [ ] Docstrings complete

### Release

- [ ] Create PR with changes
- [ ] Review and approve
- [ ] Merge to main
- [ ] Create release using new workflow (dogfooding!)
- [ ] Verify PyPI publish
- [ ] Announce new feature

---

## Conclusion

This implementation plan provides a complete roadmap for adding release workflow generation to `pypi-workflow-generator`. The design is:

- **Simple**: No new dependencies, uses built-in GitHub features
- **Comprehensive**: Covers CLI, MCP, and default behavior
- **Tested**: 8 new tests ensure quality
- **Documented**: Clear usage examples and explanations
- **Dogfooded**: We'll use it on itself to prove it works

**Key Benefits**:
- ✅ Zero-token release creation (UI-based)
- ✅ Automated version calculation
- ✅ Professional release notes
- ✅ Complete automation out-of-box
- ✅ Maintains backward compatibility

**Next Steps**:
1. Review this plan
2. Begin implementation
3. Test thoroughly
4. Dogfood on this project
5. Release and celebrate! 🎉
