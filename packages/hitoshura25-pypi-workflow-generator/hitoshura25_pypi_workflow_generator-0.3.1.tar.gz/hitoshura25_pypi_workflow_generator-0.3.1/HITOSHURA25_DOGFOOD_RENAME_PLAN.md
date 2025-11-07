# DOGFOODING PLAN: Rename to Use Auto-Detected Git Prefix `hitoshura25`

**Date:** 2025-11-06
**Goal:** Re-dogfood the project to properly demonstrate auto-detection by using the `hitoshura25` prefix detected from git remote URL
**Status:** Ready for execution

---

## Context

### Why This Rename?

Previously, we renamed the project from `pypi-workflow-generator` to `vmenon25-pypi-workflow-generator` to dogfood the prefix feature. However, this used a **manually specified prefix** (`--prefix vmenon25`) rather than demonstrating the **auto-detection** feature.

Now that PyPI and TestPyPI accounts are set up under the GitHub username `hitoshura25`, we can properly demonstrate auto-detection:

```bash
# Git remote URL
git@github.com:hitoshura25/pypi-workflow-generator.git

# Auto-detected prefix from remote URL
hitoshura25

# Final package name
hitoshura25-pypi-workflow-generator
```

This is the **ideal dogfooding scenario** because:
- ✅ No manual `--prefix` flag needed
- ✅ Shows auto-detection from GitHub remote URL
- ✅ Matches actual PyPI account username
- ✅ Demonstrates the feature working as designed

---

## Changes Overview

### File Categories

1. **Package Directory** (1 rename)
   - `vmenon25_pypi_workflow_generator/` → `hitoshura25_pypi_workflow_generator/`

2. **Configuration Files** (2 files)
   - `pyproject.toml`
   - `setup.py`

3. **Python Source Files** (~10 files)
   - All `.py` files with imports

4. **Test Files** (6 files)
   - All test imports

5. **GitHub Workflows** (3 files)
   - `.github/workflows/_reusable-test-build.yml`
   - `.github/workflows/test-pr.yml`
   - `.github/workflows/release.yml`

6. **Documentation** (2 files)
   - `README.md`
   - `hitoshura25_pypi_workflow_generator/README.md`

---

## Detailed Implementation Steps

### Step 1: Rename Package Directory

**Command:**
```bash
git mv vmenon25_pypi_workflow_generator hitoshura25_pypi_workflow_generator
```

**Effect:**
- Package directory: `vmenon25_pypi_workflow_generator/` → `hitoshura25_pypi_workflow_generator/`
- Git tracks this as a rename (preserves history)

---

### Step 2: Update `pyproject.toml`

**File:** `/Users/vinayakmenon/pypi-workflow-generator/pyproject.toml`

**Changes:**

```toml
# Line 6: Package name
name = "vmenon25-pypi-workflow-generator"
# →
name = "hitoshura25-pypi-workflow-generator"

# Lines 42-45: Entry points (console_scripts)
vmenon25-pypi-workflow-generator = "vmenon25_pypi_workflow_generator.main:main"
vmenon25-pypi-workflow-generator-init = "vmenon25_pypi_workflow_generator.init:main"
vmenon25-pypi-release = "vmenon25_pypi_workflow_generator.create_release:main"
mcp-vmenon25-pypi-workflow-generator = "vmenon25_pypi_workflow_generator.server:main"
# →
hitoshura25-pypi-workflow-generator = "hitoshura25_pypi_workflow_generator.main:main"
hitoshura25-pypi-workflow-generator-init = "hitoshura25_pypi_workflow_generator.init:main"
hitoshura25-pypi-release = "hitoshura25_pypi_workflow_generator.create_release:main"
mcp-hitoshura25-pypi-workflow-generator = "hitoshura25_pypi_workflow_generator.server:main"

# Line 52: Package finder
include = ["vmenon25_pypi_workflow_generator*"]
# →
include = ["hitoshura25_pypi_workflow_generator*"]

# Line 56: Package data
vmenon25_pypi_workflow_generator = ["*.j2"]
# →
hitoshura25_pypi_workflow_generator = ["*.j2"]
```

---

### Step 3: Update `setup.py`

**File:** `/Users/vinayakmenon/pypi-workflow-generator/setup.py`

**Changes:**

```python
# Line 18: Package name
name='vmenon25-pypi-workflow-generator',
# →
name='hitoshura25-pypi-workflow-generator',

# Lines 49-55: Entry points
'vmenon25-pypi-workflow-generator=vmenon25_pypi_workflow_generator.main:main',
'vmenon25-pypi-workflow-generator-init=vmenon25_pypi_workflow_generator.init:main',
'vmenon25-pypi-release=vmenon25_pypi_workflow_generator.create_release:main',
'vmenon25-pypi-workflow-generator-release=vmenon25_pypi_workflow_generator.release_workflow:main',
'mcp-vmenon25-pypi-workflow-generator=vmenon25_pypi_workflow_generator.server:main',
# →
'hitoshura25-pypi-workflow-generator=hitoshura25_pypi_workflow_generator.main:main',
'hitoshura25-pypi-workflow-generator-init=hitoshura25_pypi_workflow_generator.init:main',
'hitoshura25-pypi-release=hitoshura25_pypi_workflow_generator.create_release:main',
'hitoshura25-pypi-workflow-generator-release=hitoshura25_pypi_workflow_generator.release_workflow:main',
'mcp-hitoshura25-pypi-workflow-generator=hitoshura25_pypi_workflow_generator.server:main',
```

---

### Step 4: Update All Import Statements

**Pattern to Find:**
```python
from vmenon25_pypi_workflow_generator
import vmenon25_pypi_workflow_generator
```

**Replace With:**
```python
from hitoshura25_pypi_workflow_generator
import hitoshura25_pypi_workflow_generator
```

**Files Affected:**

**Source Files:**
- `hitoshura25_pypi_workflow_generator/__init__.py` (if has imports)
- `hitoshura25_pypi_workflow_generator/main.py`
- `hitoshura25_pypi_workflow_generator/init.py`
- `hitoshura25_pypi_workflow_generator/create_release.py`
- `hitoshura25_pypi_workflow_generator/release_workflow.py`
- `hitoshura25_pypi_workflow_generator/server.py`
- `hitoshura25_pypi_workflow_generator/generator.py`

**Test Files:**
- `hitoshura25_pypi_workflow_generator/tests/test_init.py`
- `hitoshura25_pypi_workflow_generator/tests/test_server.py`
- `hitoshura25_pypi_workflow_generator/tests/test_release_workflow.py`
- `hitoshura25_pypi_workflow_generator/tests/test_generator.py`
- `hitoshura25_pypi_workflow_generator/tests/test_calculate_version.py`
- `hitoshura25_pypi_workflow_generator/tests/test_git_utils.py`

---

### Step 5: Update GitHub Actions Workflows

**File 1:** `.github/workflows/_reusable-test-build.yml`

```yaml
# Line 15: Default test path
default: 'vmenon25_pypi_workflow_generator/'
# →
default: 'hitoshura25_pypi_workflow_generator/'
```

**File 2:** `.github/workflows/test-pr.yml`

```yaml
# Line 39: Test path
test_path: 'vmenon25_pypi_workflow_generator/'
# →
test_path: 'hitoshura25_pypi_workflow_generator/'
```

**File 3:** `.github/workflows/release.yml`

```yaml
# Line 56: Test path
test_path: 'vmenon25_pypi_workflow_generator/'
# →
test_path: 'hitoshura25_pypi_workflow_generator/'
```

---

### Step 6: Update Documentation

**File 1:** `README.md`

**All occurrences of:**
```
vmenon25-pypi-workflow-generator
vmenon25_pypi_workflow_generator
mcp-vmenon25-pypi-workflow-generator
```

**Replace with:**
```
hitoshura25-pypi-workflow-generator
hitoshura25_pypi_workflow_generator
mcp-hitoshura25-pypi-workflow-generator
```

**Key sections:**
- Title (line 1)
- Installation command (line 22)
- MCP configuration example (lines 37-39)
- CLI command examples (lines 50, 56, 74, 85, etc.)
- All code examples throughout

**File 2:** `hitoshura25_pypi_workflow_generator/README.md`

```markdown
# Line 1: Package name
# `vmenon25_pypi_workflow_generator` Package
# →
# `hitoshura25_pypi_workflow_generator` Package

# Line 137: Import example
from vmenon25_pypi_workflow_generator import generate_workflow, initialize_project, create_git_release
# →
from hitoshura25_pypi_workflow_generator import generate_workflow, initialize_project, create_git_release
```

---

## Verification Checklist

### Pre-Rename Verification
- [x] Git remote URL is `git@github.com:hitoshura25/pypi-workflow-generator.git`
- [x] PyPI account exists under `hitoshura25`
- [x] TestPyPI account exists under `hitoshura25`
- [x] Current tests pass (45/45)
- [x] Current package builds successfully

### Post-Rename Verification

**1. Import Verification**
```bash
# All imports should work
python -c "from hitoshura25_pypi_workflow_generator import generator"
python -c "from hitoshura25_pypi_workflow_generator.git_utils import get_git_username"
```

**2. Test Suite**
```bash
.venv/bin/pytest hitoshura25_pypi_workflow_generator/tests/ -v
# Expected: 45 passed
```

**3. Package Build**
```bash
.venv/bin/python -m build
# Expected: Successfully built hitoshura25_pypi_workflow_generator-*.tar.gz and *.whl
```

**4. Command Entry Points** (after install)
```bash
pip install -e .
hitoshura25-pypi-workflow-generator --help
hitoshura25-pypi-workflow-generator-init --help
mcp-hitoshura25-pypi-workflow-generator
```

**5. Auto-Detection Test**
```bash
# In a test directory
hitoshura25-pypi-workflow-generator-init \
  --package-name test-app \
  --author "Test" \
  --author-email "test@example.com" \
  --description "Test" \
  --url "https://github.com/test/test-app" \
  --command-name test-app

# Should auto-detect "hitoshura25" from git and create:
# - Package: hitoshura25-test-app
# - Import: hitoshura25_test_app
```

---

## Rollback Plan

If issues arise:

```bash
# Revert the rename
git mv hitoshura25_pypi_workflow_generator vmenon25_pypi_workflow_generator

# Revert all file changes
git checkout pyproject.toml setup.py README.md .github/workflows/

# Revert import changes in source files
git checkout hitoshura25_pypi_workflow_generator/
```

---

## Post-Rename Communication

### Update README Section

Add a note explaining the dogfooding:

```markdown
## About This Project

This project practices what it preaches! The package name `hitoshura25-pypi-workflow-generator`
was automatically generated using the tool's own prefix auto-detection feature:

- **Git detects:** `hitoshura25` from `git@github.com:hitoshura25/pypi-workflow-generator.git`
- **Auto-applies prefix:** Creates `hitoshura25-pypi-workflow-generator`
- **No manual override needed:** Pure auto-detection in action

This demonstrates the recommended workflow for all users of this tool.
```

---

## Success Criteria

- ✅ All 45 tests pass
- ✅ Package builds successfully
- ✅ All imports work correctly
- ✅ CLI commands are accessible
- ✅ MCP server starts without errors
- ✅ Auto-detection properly demonstrates from git remote URL
- ✅ Documentation accurately reflects new name
- ✅ GitHub workflows reference correct paths

---

## Estimated Time

- **Plan creation:** Complete
- **Execution:** ~15 minutes
- **Testing:** ~5 minutes
- **Total:** ~20 minutes

---

**END OF PLAN**
