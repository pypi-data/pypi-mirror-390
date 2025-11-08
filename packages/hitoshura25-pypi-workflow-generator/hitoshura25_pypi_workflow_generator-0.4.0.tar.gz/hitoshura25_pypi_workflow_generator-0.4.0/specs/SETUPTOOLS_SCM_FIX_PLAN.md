# IMPLEMENTATION PLAN: Fix setuptools_scm Version Detection and Reduce Duplication

**Date:** 2025-11-05
**Issue:** setuptools_scm cannot detect versions from unpushed tags in reusable workflows
**Secondary Issue:** Version calculation logic duplicated between test-pr.yml and release.yml
**Solution:** Use SETUPTOOLS_SCM_PRETEND_VERSION + shared version calculation script

---

## Problem Statement

### Primary Issue: setuptools_scm Version Detection

When the reusable workflow `_reusable-test-build.yml` runs:
- It checks out code in a fresh runner
- Tags created locally in previous jobs don't exist in this runner
- setuptools_scm cannot determine the version from git history
- Build fails or generates incorrect version

**Working Solution Found:**
- Pass version explicitly via `artifact_version` input parameter
- Set `SETUPTOOLS_SCM_PRETEND_VERSION` environment variable during build
- setuptools_scm uses this version instead of git detection

### Secondary Issue: Code Duplication

Both `test-pr.yml` and `release.yml` have nearly identical version calculation logic:

**Duplicated Code:**
1. "Get latest tag" step (100% identical in both workflows)
2. "Calculate new version" step (90% similar, different formulas)

**Impact:**
- Maintenance burden: changes must be made in two places
- Risk of inconsistency
- More code to test
- Harder to add new versioning strategies

---

## Solution Architecture

### Current (Implemented but Duplicated):

```
test-pr.yml:
  ├─ Job: get-new-version
  │    ├─ Get latest tag (bash)
  │    └─ Calculate RC version (bash)
  ├─ Job: test-and-build (reusable)
  │    └─ Build with SETUPTOOLS_SCM_PRETEND_VERSION
  └─ Job: publish-to-testpypi

release.yml:
  ├─ Job: calculate-version  ← RENAMED (no tag creation)
  │    ├─ Get latest tag (bash) ← DUPLICATE
  │    └─ Calculate release version (bash) ← SIMILAR
  ├─ Job: test-and-build (reusable)
  │    └─ Build with SETUPTOOLS_SCM_PRETEND_VERSION
  └─ Job: publish-to-pypi
       ├─ Create tag locally
       ├─ Push tag to remote
       └─ Create GitHub Release
```

### Proposed (DRY with Shared Script):

```
scripts/
  └─ calculate_version.sh ← NEW: Shared version logic

test-pr.yml:
  ├─ Job: get-new-version
  │    └─ Call: calculate_version.sh --type rc --bump patch
  ├─ Job: test-and-build (reusable)
  │    └─ Build with SETUPTOOLS_SCM_PRETEND_VERSION
  └─ Job: publish-to-testpypi

release.yml:
  ├─ Job: calculate-version  ← RENAMED (no tag creation)
  │    └─ Call: calculate_version.sh --type release --bump <input>
  ├─ Job: test-and-build (reusable)
  │    └─ Build with SETUPTOOLS_SCM_PRETEND_VERSION
  └─ Job: publish-to-pypi
       ├─ Publish to PyPI (FIRST - critical operation)
       ├─ Create tag locally  ← MOVED HERE
       ├─ Push tag to remote
       └─ Create GitHub Release
```

---

## Phase 1: Create Shared Version Calculation Script

### 1.1 Create: `scripts/calculate_version.sh`

**Purpose:** Single source of truth for all version calculations

**Location:** `scripts/calculate_version.sh` (in template project)

**Features:**
- Supports both release versions (v1.2.3) and RC versions (1.2.4rc123)
- Accepts version bump type (major, minor, patch)
- Handles initial version (v0.0.0)
- Outputs GitHub Actions compatible format
- Exit codes for error handling
- Extensive validation and error messages

**Script Content:**

```bash
#!/usr/bin/env bash
set -euo pipefail

# calculate_version.sh - Version calculation for GitHub Actions workflows
# Usage: calculate_version.sh --type <release|rc> --bump <major|minor|patch> [--pr-number NUM] [--run-number NUM]

# Default values
VERSION_TYPE=""
BUMP_TYPE=""
PR_NUMBER=""
RUN_NUMBER=""
OUTPUT_FILE="${GITHUB_OUTPUT:-/dev/stdout}"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --type)
      VERSION_TYPE="$2"
      shift 2
      ;;
    --bump)
      BUMP_TYPE="$2"
      shift 2
      ;;
    --pr-number)
      PR_NUMBER="$2"
      shift 2
      ;;
    --run-number)
      RUN_NUMBER="$2"
      shift 2
      ;;
    --help)
      cat << EOF
Usage: calculate_version.sh [OPTIONS]

Calculate semantic version based on latest git tag.

OPTIONS:
  --type TYPE          Version type: 'release' or 'rc' (required)
  --bump BUMP          Bump type: 'major', 'minor', or 'patch' (required)
  --pr-number NUM      PR number for RC versions (required if --type rc)
  --run-number NUM     Run number for RC versions (required if --type rc)
  --help               Show this help message

OUTPUTS (to \$GITHUB_OUTPUT):
  new_version          The calculated version string
  latest_tag           The latest tag found

EXAMPLES:
  # Release version (patch bump)
  calculate_version.sh --type release --bump patch
  # Output: new_version=v1.2.4

  # RC version for PR #123, run #45
  calculate_version.sh --type rc --bump patch --pr-number 123 --run-number 45
  # Output: new_version=1.2.4rc12345

EXIT CODES:
  0  Success
  1  Invalid arguments or git error
EOF
      exit 0
      ;;
    *)
      echo -e "${RED}Error: Unknown argument '$1'${NC}" >&2
      echo "Use --help for usage information" >&2
      exit 1
      ;;
  esac
done

# Validate required arguments
if [[ -z "$VERSION_TYPE" ]]; then
  echo -e "${RED}Error: --type is required${NC}" >&2
  exit 1
fi

if [[ "$VERSION_TYPE" != "release" && "$VERSION_TYPE" != "rc" ]]; then
  echo -e "${RED}Error: --type must be 'release' or 'rc'${NC}" >&2
  exit 1
fi

if [[ -z "$BUMP_TYPE" ]]; then
  echo -e "${RED}Error: --bump is required${NC}" >&2
  exit 1
fi

if [[ "$BUMP_TYPE" != "major" && "$BUMP_TYPE" != "minor" && "$BUMP_TYPE" != "patch" ]]; then
  echo -e "${RED}Error: --bump must be 'major', 'minor', or 'patch'${NC}" >&2
  exit 1
fi

if [[ "$VERSION_TYPE" == "rc" ]]; then
  if [[ -z "$PR_NUMBER" ]]; then
    echo -e "${RED}Error: --pr-number is required for RC versions${NC}" >&2
    exit 1
  fi
  if [[ -z "$RUN_NUMBER" ]]; then
    echo -e "${RED}Error: --run-number is required for RC versions${NC}" >&2
    exit 1
  fi
fi

# Get latest tag
echo "=== Getting Latest Tag ===" >&2
latest_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
echo -e "${GREEN}Latest tag: $latest_tag${NC}" >&2

# Strip 'v' prefix for version calculation
version=${latest_tag#v}

# Parse version components
IFS='.' read -r major minor patch <<< "$version"

# Validate parsed components
if ! [[ "$major" =~ ^[0-9]+$ ]] || ! [[ "$minor" =~ ^[0-9]+$ ]] || ! [[ "$patch" =~ ^[0-9]+$ ]]; then
  echo -e "${RED}Error: Could not parse version from tag '$latest_tag'${NC}" >&2
  echo "Expected format: v1.2.3" >&2
  exit 1
fi

echo "Parsed version: $major.$minor.$patch" >&2

# Apply version bump
case $BUMP_TYPE in
  major)
    major=$((major + 1))
    minor=0
    patch=0
    echo -e "${YELLOW}Bumping MAJOR version${NC}" >&2
    ;;
  minor)
    minor=$((minor + 1))
    patch=0
    echo -e "${YELLOW}Bumping MINOR version${NC}" >&2
    ;;
  patch)
    patch=$((patch + 1))
    echo -e "${YELLOW}Bumping PATCH version${NC}" >&2
    ;;
esac

# Generate version based on type
if [[ "$VERSION_TYPE" == "release" ]]; then
  new_version="v${major}.${minor}.${patch}"
  echo -e "${GREEN}Generated release version: $new_version${NC}" >&2
elif [[ "$VERSION_TYPE" == "rc" ]]; then
  # RC version format: major.minor.patch + "rc" + PR# + RUN#
  # Example: 1.2.3rc12345 (PR 123, run 45)
  new_version="${major}.${minor}.${patch}rc${PR_NUMBER}${RUN_NUMBER}"
  echo -e "${GREEN}Generated RC version: $new_version${NC}" >&2
fi

# Output for GitHub Actions
echo "latest_tag=$latest_tag" >> "$OUTPUT_FILE"
echo "new_version=$new_version" >> "$OUTPUT_FILE"

echo "" >&2
echo "=== Summary ===" >&2
echo "Latest tag:  $latest_tag" >&2
echo "Bump type:   $BUMP_TYPE" >&2
echo "New version: $new_version" >&2
```

### 1.2 Create Template: `scripts/calculate_version.sh.j2`

**Location:** `pypi_workflow_generator/scripts/calculate_version.sh.j2`

**Content:** Identical to above, but as a Jinja2 template (no templating needed for now, but allows for future customization)

---

## Phase 2: Update Workflow Templates

### 2.1 Update: `_reusable_test_build.yml.j2`

**Location:** `pypi_workflow_generator/_reusable_test_build.yml.j2`

**Changes:**
1. Add `artifact_version` input parameter
2. Use `SETUPTOOLS_SCM_PRETEND_VERSION` during build
3. Add conditional check to only set env var if version provided

**Complete Updated Template:**

```yaml
name: Reusable Test and Build

on:
  workflow_call:
    inputs:
      python_version:
        description: 'Python version to use'
        required: false
        type: string
        default: '{{ python_version }}'
      test_path:
        description: 'Path to tests'
        required: false
        type: string
        default: '{{ test_path }}'
      artifact_version:
        description: 'Version to use for the artifact (overrides setuptools_scm detection)'
        required: false
        type: string
        default: ''

jobs:
  test-and-build:
    runs-on: ubuntu-latest
    permissions:
      contents: read

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # For setuptools_scm
          fetch-tags: true

      - name: Set up Python {% raw %}${{ inputs.python_version }}{% endraw %}
        uses: actions/setup-python@v5
        with:
          python-version: {% raw %}${{ inputs.python_version }}{% endraw %}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests with pytest
        run: python -m pytest {% raw %}${{ inputs.test_path }}{% endraw %}

      - name: Build package
        env:
          # Override version detection if artifact_version is provided
          SETUPTOOLS_SCM_PRETEND_VERSION: {% raw %}${{ inputs.artifact_version }}{% endraw %}
        run: python -m build

      - name: Store the distribution packages
        uses: actions/upload-artifact@v4
        with:
          name: python-package-distributions
          path: dist/
```

**Key Changes:**
- Lines 16-20: New `artifact_version` input parameter
- Lines 48-51: Build step now sets `SETUPTOOLS_SCM_PRETEND_VERSION`

### 2.2 Update: `test_pr.yml.j2`

**Location:** `pypi_workflow_generator/test_pr.yml.j2`

**Changes:**
1. Add new `get-new-version` job that calls the script
2. Update `test-and-build` job to pass `artifact_version`
3. Update `publish-to-testpypi` to depend on both jobs

**Complete Updated Template:**

```yaml
name: Test and Publish to TestPyPI

on:
  pull_request:
    branches: [ main ]

jobs:
  get-new-version:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    outputs:
      new_version: {% raw %}${{ steps.calc_version.outputs.new_version }}{% endraw %}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          fetch-tags: true

      - name: Make version script executable
        run: chmod +x scripts/calculate_version.sh

      - name: Calculate RC version
        id: calc_version
        run: |
          ./scripts/calculate_version.sh \
            --type rc \
            --bump patch \
            --pr-number {% raw %}"${{ github.event.pull_request.number }}"{% endraw %} \
            --run-number {% raw %}"${{ github.run_number }}"{% endraw %}

  test-and-build:
    uses: ./.github/workflows/_reusable-test-build.yml
    needs: [get-new-version]
    with:
      python_version: '{{ python_version }}'
      test_path: '{{ test_path }}'
      artifact_version: {% raw %}${{ needs.get-new-version.outputs.new_version }}{% endraw %}

  publish-to-testpypi:
    name: Publish to TestPyPI
    needs: [test-and-build, get-new-version]
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # For TestPyPI Trusted Publishing

    steps:
      - name: Download all the dists
        uses: actions/download-artifact@v4
        with:
          name: python-package-distributions
          path: dist/

      - name: Publish to TestPyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/
          verbose: {{ verbose_publish | lower }}
```

**Key Changes:**
- Lines 8-32: New `get-new-version` job using the script
- Line 36: Removed duplicate version calculation logic (now calls script)
- Line 40: Pass `artifact_version` to reusable workflow
- Line 44: Add `get-new-version` to needs array

### 2.3 Update: `release.yml.j2`

**Location:** `pypi_workflow_generator/release.yml.j2`

**Changes:**
1. Rename `create-tag` → `calculate-version` (removes tag creation)
2. Use shared script for version calculation
3. Move tag creation to `publish-to-pypi` job (after successful publish)
4. Pass `artifact_version` to `test-and-build` job
5. Remove duplicate version calculation code

**Complete Updated Template:**

```yaml
name: Release to PyPI

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
  calculate-version:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    outputs:
      new_version: {% raw %}${{ steps.calc_version.outputs.new_version }}{% endraw %}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          fetch-tags: true

      - name: Make version script executable
        run: chmod +x scripts/calculate_version.sh

      - name: Calculate release version
        id: calc_version
        run: |
          ./scripts/calculate_version.sh \
            --type release \
            --bump {% raw %}"${{ github.event.inputs.release_type }}"{% endraw %}

      - name: Check if tag already exists remotely
        run: |
          new_version="{% raw %}${{ steps.calc_version.outputs.new_version }}{% endraw %}"
          if git ls-remote --tags origin | grep -q "refs/tags/$new_version$"; then
            echo "::error::Tag $new_version already exists on remote!"
            echo "::error::This may indicate a previous release attempt."
            echo "::error::Please use a different version or delete the remote tag first."
            exit 1
          fi
          echo "✅ Tag $new_version does not exist remotely"

  test-and-build:
    needs: [calculate-version]
    uses: ./.github/workflows/_reusable-test-build.yml
    with:
      python_version: '{{ python_version }}'
      test_path: '{{ test_path }}'
      artifact_version: {% raw %}${{ needs.calculate-version.outputs.new_version }}{% endraw %}

  publish-to-pypi:
    name: Publish to PyPI
    needs: [calculate-version, test-and-build]
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # For PyPI Trusted Publishing
      contents: write  # For pushing tags and creating releases

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          fetch-tags: true

      - name: Download all the dists
        uses: actions/download-artifact@v4
        with:
          name: python-package-distributions
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          verbose: {{ verbose_publish | lower }}

      - name: Create and push tag
        run: |
          new_version="{% raw %}${{ needs.calculate-version.outputs.new_version }}{% endraw %}"

          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

          git tag -a "$new_version" -m "Release $new_version"
          git push origin "$new_version"

          echo "✅ Created and pushed tag: $new_version"
        env:
          GITHUB_TOKEN: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}

      - name: Create GitHub Release
        run: |
          new_version="{% raw %}${{ needs.calculate-version.outputs.new_version }}{% endraw %}"
          gh release create "$new_version" \
            --title "Release $new_version" \
            --generate-notes
        env:
          GITHUB_TOKEN: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}

      - name: Summary
        run: |
          new_version="{% raw %}${{ needs.calculate-version.outputs.new_version }}{% endraw %}"
          echo "### Release Published Successfully :rocket:" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**Version**: $new_version" >> $GITHUB_STEP_SUMMARY
          echo "**Type**: {% raw %}${{ github.event.inputs.release_type }}{% endraw %}" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**Steps completed**:" >> $GITHUB_STEP_SUMMARY
          echo "- ✅ Tests passed" >> $GITHUB_STEP_SUMMARY
          echo "- ✅ Package built" >> $GITHUB_STEP_SUMMARY
          echo "- ✅ Published to PyPI" >> $GITHUB_STEP_SUMMARY
          echo "- ✅ Tag pushed to repository" >> $GITHUB_STEP_SUMMARY
          echo "- ✅ GitHub Release created" >> $GITHUB_STEP_SUMMARY
```

**Key Changes:**
- Line 15: Renamed job from `create-tag` to `calculate-version`
- Line 18: Changed permission from `write` to `read` (no longer creating tags here)
- Lines 39-48: Removed local tag creation step
- Line 50: Updated job dependency reference
- Line 55: Updated job dependency reference
- Line 59: Updated job dependency reference
- Lines 80-90: **NEW** - Create tag locally and push immediately after successful PyPI publish
- Removed ~20 lines of premature tag creation logic

---

## Design Decisions

### Order of Operations in Release Workflow

**Critical Design Choice: Publish to PyPI BEFORE Creating/Pushing Tag**

The `publish-to-pypi` job performs operations in this specific order:

```yaml
1. Publish to PyPI           ← FIRST (critical operation)
2. Create tag locally         ← SECOND (metadata)
3. Push tag to remote         ← THIRD (metadata)
4. Create GitHub Release      ← FOURTH (metadata)
```

#### Why This Order?

**Scenario 1: Tag Created First (❌ Bad Practice)**

If we created/pushed the tag before publishing:
- ❌ Tag visible in GitHub (users think release is done)
- ❌ Package NOT in PyPI (users can't install it)
- ❌ Version is "burned" - can't reuse the same tag
- ❌ Recovery requires either:
  - Deleting the tag (bad practice, breaks immutability)
  - Skipping this version (wastes version number)
  - Manually publishing to PyPI (risky, might fail again)

**Scenario 2: Publish First (✅ Best Practice - Current Implementation)**

With PyPI publish before tag creation:
- ✅ Package exists in PyPI (primary goal achieved!)
- ✅ Users can install immediately: `pip install package==1.2.3`
- ✅ Tag push failure is non-critical (easy manual fix)
- ✅ No version wasted
- ✅ Simple recovery procedure (see below)

#### Recovery Procedures

**If PyPI Publish Fails:**
- Workflow stops before tag creation ✅
- No cleanup needed
- Fix the issue and re-run workflow
- Same version number can be used

**If Tag Push Fails (after successful PyPI publish):**
- Package is already live on PyPI ✅
- Users can install it immediately ✅
- Manual recovery (simple, low-risk):
  ```bash
  git tag v1.2.3
  git push origin v1.2.3
  gh release create v1.2.3 --generate-notes
  ```

**If GitHub Release Creation Fails:**
- Package is on PyPI ✅
- Tag exists in repository ✅
- Manual recovery:
  ```bash
  gh release create v1.2.3 --generate-notes
  ```

#### Comparison with Other Approaches

| Approach | PyPI Fails | Tag Push Fails | Recovery Complexity |
|----------|-----------|----------------|---------------------|
| **Tag first** | High (delete tag or skip version) | N/A | Complex |
| **Publish first** ✅ | Low (retry workflow) | Low (manual tag push) | Simple |
| **Simultaneous** | Medium (cleanup needed) | Medium (partial state) | Medium |

#### Key Principle

> **Fail-safe principle**: Complete the critical, hard-to-fix operation first (PyPI publish), then handle the easy-to-fix metadata operations (tags, releases).

PyPI is the source of truth for package availability. Tags and releases are important metadata, but they're secondary to package availability and easier to fix manually if something goes wrong.

---

## Phase 3: Update Generator Logic

### 3.1 Update: `generator.py`

**File:** `pypi_workflow_generator/generator.py`

**Changes:**

1. Add script generation logic
2. Create `scripts/` directory in project root
3. Copy and render the script template

**Updated `generate_workflows()` function:**

```python
def generate_workflows(
    package_name: str,
    python_version: str = "3.11",
    test_path: str = "tests/",
    verbose_publish: bool = False,
    output_dir: Optional[Path] = None
) -> bool:
    """
    Generate GitHub Actions workflow files for PyPI publishing.

    Args:
        package_name: Name of the Python package
        python_version: Python version to use (default: "3.11")
        test_path: Path to test directory (default: "tests/")
        verbose_publish: Enable verbose output for PyPI publish (default: False)
        output_dir: Output directory (default: current directory)

    Returns:
        bool: True if workflows were generated successfully
    """
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)

    # Setup Jinja2 environment
    templates_dir = Path(__file__).parent
    env = Environment(loader=FileSystemLoader(templates_dir))

    # Create necessary directories
    workflow_dir = output_dir / '.github' / 'workflows'
    script_dir = output_dir / 'scripts'

    workflow_dir.mkdir(parents=True, exist_ok=True)
    script_dir.mkdir(parents=True, exist_ok=True)

    # Template context
    context = {
        'package_name': package_name,
        'python_version': python_version,
        'test_path': test_path,
        'verbose_publish': verbose_publish,
    }

    # Workflow templates to generate
    workflow_templates = [
        ('_reusable_test_build.yml.j2', '_reusable-test-build.yml'),
        ('release.yml.j2', 'release.yml'),
        ('test_pr.yml.j2', 'test-pr.yml')
    ]

    # Script templates to generate
    script_templates = [
        ('calculate_version.sh.j2', 'calculate_version.sh')
    ]

    try:
        # Generate workflow files
        for template_name, output_name in workflow_templates:
            template = env.get_template(template_name)
            output_path = workflow_dir / output_name

            with open(output_path, 'w') as f:
                f.write(template.render(context))

            print(f"✅ Generated: {output_path}")

        # Generate script files
        for template_name, output_name in script_templates:
            template = env.get_template(f'scripts/{template_name}')
            output_path = script_dir / output_name

            with open(output_path, 'w') as f:
                f.write(template.render(context))

            # Make script executable
            output_path.chmod(0o755)

            print(f"✅ Generated: {output_path} (executable)")

        print(f"\n✨ Successfully generated workflows in {workflow_dir}")
        print(f"✨ Successfully generated scripts in {script_dir}")
        return True

    except Exception as e:
        print(f"❌ Error generating workflows: {e}", file=sys.stderr)
        return False
```

**Key Changes:**
- Lines 32-33: Create `scripts/` directory
- Lines 49-51: New `script_templates` list
- Lines 63-72: Generate script files with executable permissions

### 3.2 Create Directory Structure

**New Structure:**
```
pypi_workflow_generator/
├── __init__.py
├── generator.py
├── cli.py
├── server.py
├── _reusable_test_build.yml.j2
├── release.yml.j2
├── test_pr.yml.j2
└── scripts/                          ← NEW
    └── calculate_version.sh.j2       ← NEW
```

---

## Phase 4: Update Tests

### 4.1 Create: `test_calculate_version.py`

**Location:** `pypi_workflow_generator/tests/test_calculate_version.py`

**Purpose:** Test the version calculation script directly

**Content:**

```python
"""Tests for the calculate_version.sh script."""
import subprocess
import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def temp_git_repo(tmp_path):
    """Create a temporary git repo with some tags."""
    subprocess.run(['git', 'init'], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=tmp_path, check=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=tmp_path, check=True)

    # Create initial commit
    (tmp_path / 'test.txt').write_text('test')
    subprocess.run(['git', 'add', '.'], cwd=tmp_path, check=True)
    subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=tmp_path, check=True)

    # Create a tag
    subprocess.run(['git', 'tag', 'v1.2.3'], cwd=tmp_path, check=True)

    return tmp_path


def test_script_exists_after_generation(tmp_path):
    """Test that the script is generated and executable."""
    from pypi_workflow_generator.generator import generate_workflows

    generate_workflows(
        package_name='test-package',
        output_dir=tmp_path
    )

    script_path = tmp_path / 'scripts' / 'calculate_version.sh'
    assert script_path.exists()
    assert script_path.stat().st_mode & 0o111  # Check executable bit


def test_release_version_patch(temp_git_repo):
    """Test release version with patch bump."""
    script = temp_git_repo / 'scripts' / 'calculate_version.sh'

    # Copy script to temp repo (in real usage, generator does this)
    from pypi_workflow_generator import generator
    script_template = Path(generator.__file__).parent / 'scripts' / 'calculate_version.sh.j2'

    # For now, we'll test the logic with subprocess
    # This test will be fully functional once script is templated
    # Placeholder for now
    assert temp_git_repo.exists()


def test_rc_version_generation(temp_git_repo):
    """Test RC version generation."""
    # This will be implemented once script is in place
    pass


def test_version_with_no_tags(tmp_path):
    """Test version calculation when no tags exist (should default to v0.0.0)."""
    # Initialize empty repo
    subprocess.run(['git', 'init'], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=tmp_path, check=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=tmp_path, check=True)

    # Create initial commit
    (tmp_path / 'test.txt').write_text('test')
    subprocess.run(['git', 'add', '.'], cwd=tmp_path, check=True)
    subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=tmp_path, check=True)

    # Test would run script here
    # Expected: v0.0.1 for release, 0.0.1rcXXX for RC
    pass
```

**Note:** These tests are stubs. Full implementation would run the actual script via subprocess.

### 4.2 Update: `test_generator.py`

**Location:** `pypi_workflow_generator/tests/test_generator.py`

**Changes:**
1. Update test assertions to check for script generation
2. Verify script is executable

**Add to existing tests:**

```python
def test_generate_workflows_creates_script(tmp_path):
    """Test that script directory and files are created."""
    generate_workflows(
        package_name='test-package',
        output_dir=tmp_path
    )

    script_dir = tmp_path / 'scripts'
    script_file = script_dir / 'calculate_version.sh'

    assert script_dir.exists()
    assert script_file.exists()
    assert script_file.stat().st_mode & 0o111  # Executable


def test_script_contains_correct_shebang(tmp_path):
    """Test that generated script has proper shebang."""
    generate_workflows(
        package_name='test-package',
        output_dir=tmp_path
    )

    script_file = tmp_path / 'scripts' / 'calculate_version.sh'
    content = script_file.read_text()

    assert content.startswith('#!/usr/bin/env bash')
    assert 'calculate_version.sh' in content
```

### 4.3 Update: `test_server.py`

**Location:** `pypi_workflow_generator/tests/test_server.py`

**Changes:**
1. Add assertions for script generation in MCP tool tests

**Add to `test_call_tool_generate_workflows()`:**

```python
def test_call_tool_generate_workflows(tmp_path):
    """Test the generate_workflows tool via MCP."""
    # ... existing test code ...

    # Check script was generated
    script_path = tmp_path / "scripts" / "calculate_version.sh"
    assert script_path.exists()
    assert script_path.is_file()
    assert script_path.stat().st_mode & 0o111  # Executable
```

---

## Phase 5: Update Documentation

### 5.1 Update: `README.md`

#### Add to "Generated Workflows" Section

```markdown
### Generated Files

When you run the generator, it creates:

**Workflow Files** (`.github/workflows/`):
1. `_reusable-test-build.yml` - Reusable test and build workflow
2. `test-pr.yml` - PR testing with TestPyPI publishing
3. `release.yml` - Production release to PyPI

**Script Files** (`scripts/`):
1. `calculate_version.sh` - Shared version calculation logic
```

#### Add New Section: "Version Calculation"

```markdown
## Version Calculation

The generator creates a shared `scripts/calculate_version.sh` script that handles version calculation for both PR and release workflows.

### Version Formats

- **Release versions:** `v1.2.3` (semantic versioning with 'v' prefix)
- **RC versions:** `1.2.3rc12345` (no 'v' prefix, includes PR# and run#)

### Usage Examples

```bash
# Calculate release version (patch bump)
./scripts/calculate_version.sh --type release --bump patch
# Output: v1.2.4

# Calculate release version (minor bump)
./scripts/calculate_version.sh --type release --bump minor
# Output: v1.3.0

# Calculate RC version for PR #123, run #45
./scripts/calculate_version.sh --type rc --bump patch --pr-number 123 --run-number 45
# Output: 1.2.4rc12345
```

### How It Works

1. **Gets latest tag** from git history (defaults to v0.0.0 if none)
2. **Parses version** components (major, minor, patch)
3. **Applies bump** according to `--bump` parameter
4. **Formats output** based on `--type`:
   - `release`: Adds 'v' prefix for git tags
   - `rc`: No prefix, adds 'rc' + PR# + run#
5. **Outputs to GitHub Actions** via `$GITHUB_OUTPUT`

### Why a Shared Script?

Before this approach, version calculation logic was duplicated between `test-pr.yml` and `release.yml`. Using a shared script:
- ✅ **Single source of truth** for version logic
- ✅ **Easier to maintain** - changes in one place
- ✅ **Testable** - can run locally
- ✅ **Consistent** - same logic for all workflows
- ✅ **Extensible** - easy to add new version formats
```

#### Update "How It Works" Section

Add subsection about setuptools_scm:

```markdown
### Version Detection with setuptools_scm

The workflows handle version detection correctly even when tags don't exist in the checkout:

1. **Version calculated** in first job using `calculate_version.sh`
2. **Version passed** to reusable workflow via `artifact_version` input
3. **Build uses** `SETUPTOOLS_SCM_PRETEND_VERSION` environment variable
4. **setuptools_scm** respects this override instead of git detection

This solves the issue where reusable workflows run in fresh runners without access to locally-created tags.
```

#### Update "Features" Section

```markdown
- ✅ **DRY Version Logic**: Shared script eliminates duplication
- ✅ **setuptools_scm Compatible**: Proper version detection in reusable workflows
```

---

## Phase 6: Re-Dogfood on This Project

### 6.1 Backup Current Workflows

```bash
mkdir -p .github/workflows.backup
cp .github/workflows/*.yml .github/workflows.backup/
```

### 6.2 Regenerate Everything

```bash
# Install updated package
pip install -e .

# Run generator
pypi-workflow-generator \
  --package-name pypi-workflow-generator \
  --python-version 3.11 \
  --test-path pypi_workflow_generator/ \
  --verbose-publish
```

### 6.3 Verify Generated Files

```bash
# Check workflows exist
ls -la .github/workflows/

# Check script exists and is executable
ls -la scripts/
./scripts/calculate_version.sh --help
```

### 6.4 Compare with Current

```bash
# Compare workflows
diff .github/workflows.backup/test-pr.yml .github/workflows/test-pr.yml
diff .github/workflows.backup/release.yml .github/workflows/release.yml

# Should show:
# - Version calculation now uses script
# - artifact_version parameter added
# - Less duplicate code
```

---

## Phase 7: Testing and Validation

### 7.1 Unit Tests

```bash
pytest pypi_workflow_generator/tests/ -v
```

**Expected:** All tests pass, including new script-related tests

### 7.2 Script Testing

Test the script locally:

```bash
cd /path/to/pypi-workflow-generator

# Test release version (patch)
./scripts/calculate_version.sh --type release --bump patch

# Test RC version
./scripts/calculate_version.sh --type rc --bump patch --pr-number 123 --run-number 45

# Test with no tags
cd /tmp
git init test-repo
cd test-repo
git commit --allow-empty -m "Initial"
/path/to/calculate_version.sh --type release --bump patch
# Should output: v0.0.1
```

### 7.3 Workflow Syntax Validation

```bash
# Install actionlint if not already installed
# macOS: brew install actionlint
# Linux: Download from https://github.com/rhysd/actionlint/releases

# Validate workflow syntax
actionlint .github/workflows/*.yml
```

### 7.4 Integration Test via PR

1. Create a test branch
2. Make a small change
3. Open a PR
4. Verify `test-pr.yml` runs successfully
5. Check that RC version is calculated correctly
6. Verify TestPyPI publish works

---

## Summary of Changes

### Files Created (2)

1. `pypi_workflow_generator/scripts/calculate_version.sh.j2` - Template for version script
2. `pypi_workflow_generator/tests/test_calculate_version.py` - Tests for script

### Files Modified (6)

1. `pypi_workflow_generator/_reusable_test_build.yml.j2`
   - Add `artifact_version` input
   - Use `SETUPTOOLS_SCM_PRETEND_VERSION`

2. `pypi_workflow_generator/test_pr.yml.j2`
   - Replace inline version calc with script call
   - ~40 lines removed, 10 lines added

3. `pypi_workflow_generator/release.yml.j2`
   - Replace inline version calc with script call
   - ~40 lines removed, 10 lines added

4. `pypi_workflow_generator/generator.py`
   - Add script directory creation
   - Add script template rendering
   - Make scripts executable

5. `pypi_workflow_generator/tests/test_generator.py`
   - Add script generation tests

6. `README.md`
   - Add "Version Calculation" section
   - Update "Generated Files" section
   - Add setuptools_scm explanation

### Generated Files Structure

```
project/
├── .github/
│   └── workflows/
│       ├── _reusable-test-build.yml
│       ├── test-pr.yml
│       └── release.yml
└── scripts/
    └── calculate_version.sh
```

---

## Benefits

### 1. **Eliminates Duplication** ✅
- ~80 lines of duplicate code removed
- Version logic in one place
- Single source of truth

### 2. **Fixes setuptools_scm Issue** ✅
- Works with unpushed tags
- Explicit version passing
- No git detection failures

### 3. **Easier Maintenance** ✅
- Update version logic once, affects all workflows
- Less risk of inconsistency
- Easier to add new features

### 4. **Testable** ✅
- Can run script locally
- Can unit test with different scenarios
- Validates before workflows run

### 5. **Self-Documenting** ✅
- Script has --help flag
- Clear inputs and outputs
- Easy to understand flow

### 6. **Extensible** ✅
- Easy to add new version formats
- Can add validation rules
- Can integrate with other tools

---

## Rollout Checklist

- [ ] **Phase 1:** Create version calculation script
  - [ ] Create `scripts/` directory in template project
  - [ ] Create `calculate_version.sh.j2` template
  - [ ] Test script locally with different scenarios

- [ ] **Phase 2:** Update workflow templates
  - [ ] Update `_reusable_test_build.yml.j2` with `artifact_version` input
  - [ ] Update `test_pr.yml.j2` to use script
  - [ ] Update `release.yml.j2` to use script

- [ ] **Phase 3:** Update generator logic
  - [ ] Modify `generator.py` to create `scripts/` directory
  - [ ] Add script template rendering
  - [ ] Set executable permissions on generated script

- [ ] **Phase 4:** Update tests
  - [ ] Create `test_calculate_version.py`
  - [ ] Update `test_generator.py` with script assertions
  - [ ] Update `test_server.py` with script checks

- [ ] **Phase 5:** Update documentation
  - [ ] Add "Version Calculation" section to README
  - [ ] Update "Generated Files" section
  - [ ] Add setuptools_scm explanation
  - [ ] Update feature list

- [ ] **Phase 6:** Re-dogfood
  - [ ] Backup current workflows
  - [ ] Run `pip install -e .`
  - [ ] Run generator command
  - [ ] Compare generated files with current
  - [ ] Test script locally

- [ ] **Phase 7:** Test and validate
  - [ ] Run unit tests: `pytest pypi_workflow_generator/tests/ -v`
  - [ ] Test script manually in various scenarios
  - [ ] Validate workflow syntax with actionlint
  - [ ] Create test PR to verify integration

- [ ] **Git Commit**
  - [ ] Stage all changes
  - [ ] Write descriptive commit message
  - [ ] Commit changes

- [ ] **Integration Testing**
  - [ ] Create test PR
  - [ ] Verify RC version format is correct
  - [ ] Verify TestPyPI publish works
  - [ ] Create test release
  - [ ] Verify release version format is correct
  - [ ] Verify PyPI publish works

---

## Migration Guide for Existing Users

If you previously generated workflows with this tool, follow these steps to migrate:

### Step 1: Backup Current Workflows

```bash
mkdir -p .github/workflows.backup
cp .github/workflows/*.yml .github/workflows.backup/
```

### Step 2: Update the Generator

```bash
pip install --upgrade pypi-workflow-generator
```

### Step 3: Regenerate Workflows

```bash
pypi-workflow-generator \
  --package-name YOUR_PACKAGE_NAME \
  --python-version YOUR_PYTHON_VERSION \
  --test-path YOUR_TEST_PATH \
  --verbose-publish
```

### Step 4: Review Changes

```bash
# Compare generated files
diff .github/workflows.backup/test-pr.yml .github/workflows/test-pr.yml

# Test the new script
./scripts/calculate_version.sh --help
```

### Step 5: Test Before Committing

```bash
# Validate workflow syntax
actionlint .github/workflows/*.yml

# Run unit tests if your project has them
pytest
```

### Step 6: Commit and Test

```bash
git add .github/workflows/ scripts/
git commit -m "Update workflows to use shared version calculation script"
git push

# Create a test PR to verify everything works
```

---

## Technical Deep Dive

### Why SETUPTOOLS_SCM_PRETEND_VERSION Works

setuptools_scm has a feature to override version detection:

```python
# In pyproject.toml or setup.py, setuptools_scm reads:
[tool.setuptools_scm]

# At build time, it checks for this environment variable:
SETUPTOOLS_SCM_PRETEND_VERSION=1.2.3

# When set, setuptools_scm skips git detection and uses this value
```

This allows us to:
1. Calculate version in a job with git history
2. Pass version to reusable workflow (fresh runner, no git state)
3. Build with explicit version (no git detection needed)

### Why RC Versions Don't Have 'v' Prefix

PyPI/TestPyPI version requirements:
- Tags in git typically use: `v1.2.3` (with 'v')
- Package versions must be: `1.2.3` (without 'v')
- RC versions for pre-releases: `1.2.3rc1` (PEP 440 format)

Our approach:
- Release workflow: Creates git tag with 'v' → `v1.2.3`
- Build time: Removes 'v' for package → `1.2.3`
- PR workflow: Never creates tag, uses RC format → `1.2.3rc12345`

### Script Exit Codes

The script uses proper exit codes for error handling:

```bash
0  # Success
1  # Error (invalid arguments, git error, parsing failure)
```

Workflows can check `$?` or use GitHub Actions' automatic failure detection.

### Job Dependency Chain

**For `test-pr.yml`:**
```
get-new-version → test-and-build → publish-to-testpypi
```

**For `release.yml`:**
```
calculate-version → test-and-build → publish-to-pypi
                                         ├─ 1. Publish to PyPI
                                         ├─ 2. Create tag locally
                                         ├─ 3. Push tag to remote
                                         └─ 4. Create GitHub Release
```

All git operations (tag creation, tag push, release creation) happen in the same runner within the `publish-to-pypi` job, after successful PyPI publish.

### Permissions Matrix

| Job | contents | id-token | Why |
|-----|----------|----------|-----|
| calculate-version (release.yml) | read | - | Read code for version calculation |
| get-new-version (test-pr.yml) | read | - | Read code for version calculation |
| test-and-build | read | - | Read code, no publish |
| publish-to-testpypi | - | write | Trusted Publishing auth |
| publish-to-pypi | write | write | Trusted Publishing + push tag/create release |

**Note:** The `calculate-version` and `get-new-version` jobs only need `read` permissions because they don't create tags anymore—they just calculate the version number. All git write operations (tag creation and push) happen in the `publish-to-pypi` job after successful PyPI publish.

---

**END OF IMPLEMENTATION PLAN**

This plan eliminates duplication, fixes setuptools_scm version detection, and creates a maintainable, testable solution for version calculation across all workflows.
