# Single Workflow Consolidation Plan

## Executive Summary

**Goal:** Consolidate the two-workflow architecture into a simpler, single-workflow pattern using GitHub's reusable workflows feature to avoid duplication and encourage composition.

**Key Benefits:**
- ✅ **Zero PAT/GitHub App setup required** - Uses only default `GITHUB_TOKEN`
- ✅ **DRY principle** - Common logic (test, build, publish) defined once
- ✅ **Composition over duplication** - Reusable workflow called from multiple triggers
- ✅ **Maintainability** - Changes to build/test/publish happen in one place
- ✅ **Clear separation of concerns** - Each workflow has a single responsibility

**Trade-off:**
- ⚠️ Loses tag-based triggering - Can't manually push tags to trigger publish
- ⚠️ Must use GitHub UI for all releases

**Key Design Decision:**
- ✅ **Test/build before pushing tag** - Tag is created locally first, then pushed only if build/test succeed. This prevents orphaned tags for failed releases.

## Current Architecture Problems

### Problem 1: Token Requirement
- Two separate workflows (create-release.yml → pypi-publish.yml)
- Requires PAT or GitHub App to trigger second workflow
- Per-repo setup burden alongside PyPI Trusted Publisher

### Problem 2: Duplication
- Test/build/publish logic exists in `pypi-publish.yml`
- Would need to be duplicated if we made a single monolithic workflow
- Maintenance burden: changes must be applied in multiple places

### Problem 3: Complexity
- Users must understand workflow chaining
- Two files to manage
- Debugging requires following workflow chain

### Problem 4: Unsafe Tag Creation
- Current workflow creates and pushes tag BEFORE testing/building
- If build fails, tag already exists pointing to broken code
- Requires manual cleanup to retry

## Proposed Architecture

### Overview

Use **GitHub Actions Reusable Workflows** to compose functionality:

```
┌─────────────────────────────────────────────────────────────┐
│ release.yml (workflow_dispatch)                             │
│   1. Calculate next version                                 │
│   2. Check tag doesn't exist                                │
│   3. Create git tag LOCALLY (don't push yet)                │
│   4. Call reusable workflow ──────────────────┐             │
│      (tests/builds using local tag) ────────────┐           │
│   5. If successful, push tag & create release   │           │
└──────────────────────────────────────────────┼──┼───────────┘
                                               │  │
                                               │  │
┌──────────────────────────────────────────────┼──┼───────────┐
│ test-pr.yml (pull_request)                   │  │           │
│   Call reusable workflow ────────────────────┘  │           │
└─────────────────────────────────────────────────┼───────────┘
                                                  │
                                                  ▼
                        ┌───────────────────────────────────────┐
                        │ _reusable-build-publish.yml           │
                        │   1. Checkout code                    │
                        │   2. Setup Python                     │
                        │   3. Install dependencies             │
                        │   4. Run tests                        │
                        │   5. Build package                    │
                        │   6. Publish (PyPI or TestPyPI)       │
                        └───────────────────────────────────────┘

Key: Local tag is visible to setuptools_scm during build, but only
     pushed to remote if all tests/builds succeed. This prevents
     orphaned tags pointing to broken code.
```

### File Structure

```
.github/workflows/
├── _reusable-build-publish.yml   # Reusable workflow (core logic)
├── release.yml                    # Manual release trigger
└── test-pr.yml                    # PR testing trigger
```

**Convention:** Prefix reusable workflows with `_` to indicate they're not directly runnable.

## Detailed Design

### 1. Reusable Workflow: _reusable-build-publish.yml

**Purpose:** Contains all common logic for testing, building, and publishing.

**Inputs:**
- `publish_target`: "pypi" | "testpypi" | "none" (for testing without publish)
- `python_version`: Python version to use (default from template)
- `test_path`: Path to tests (default from template)

**Secrets:**
- None required! Uses PyPI Trusted Publishing (OIDC)

**Implementation:**

```yaml
name: Reusable Build and Publish

on:
  workflow_call:
    inputs:
      publish_target:
        description: 'Where to publish: pypi, testpypi, or none'
        required: true
        type: string
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
      ref:
        description: 'Git ref to checkout (tag, branch, or commit)'
        required: false
        type: string
        default: ''

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # Required for PyPI Trusted Publishing
      contents: read

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          ref: {% raw %}${{ inputs.ref || github.ref }}{% endraw %}
          fetch-depth: 0  # For setuptools_scm
          fetch-tags: true

      - name: Debug git state for version detection
        run: |
          echo "=== Git Describe Output ==="
          git describe --tags --long --dirty --always
          echo ""
          echo "=== Current HEAD ==="
          git rev-parse HEAD
          echo ""
          echo "=== All Tags (last 10) ==="
          git tag -l | sort -V | tail -10
          echo ""
          echo "=== Tags at HEAD ==="
          git tag --points-at HEAD
          echo ""
          echo "=== GitHub Context ==="
          echo "github.ref: {% raw %}${{ github.ref }}{% endraw %}"
          echo "github.sha: {% raw %}${{ github.sha }}{% endraw %}"
          echo "Checkout ref: {% raw %}${{ inputs.ref || github.ref }}{% endraw %}"

      - name: Set up Python {% raw %}${{ inputs.python_version }}{% endraw %}
        uses: actions/setup-python@v4
        with:
          python-version: {% raw %}${{ inputs.python_version }}{% endraw %}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests with pytest
        run: python -m pytest {% raw %}${{ inputs.test_path }}{% endraw %}

      - name: Build package
        run: python -m build

      - name: Set IS_PULL_REQUEST environment variable
        if: github.event_name == 'pull_request'
        run: echo "IS_PULL_REQUEST=true" >> $GITHUB_ENV

      - name: Publish to TestPyPI
        if: inputs.publish_target == 'testpypi'
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/
          verbose: {{ verbose_publish | lower }}

      - name: Publish to PyPI
        if: inputs.publish_target == 'pypi'
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          verbose: {{ verbose_publish | lower }}
```

**Key Design Decisions:**
- ✅ **Parameterized publish target** - Caller decides where to publish
- ✅ **Optional ref input** - Allows caller to specify exact git ref
- ✅ **No secrets** - Uses PyPI Trusted Publishing exclusively
- ✅ **Single responsibility** - Only handles build/test/publish
- ✅ **Debugging output** - Maintains git state visibility for troubleshooting

### 2. Release Workflow: release.yml

**Purpose:** Manual workflow for creating releases and publishing to PyPI.

**Trigger:** `workflow_dispatch` (GitHub UI button)

**Implementation:**

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
  release-and-publish:
    runs-on: ubuntu-latest
    permissions:
      contents: write  # For pushing tags and creating releases
      id-token: write  # For PyPI Trusted Publishing

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
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
          latest_tag="{% raw %}${{ steps.get_latest_tag.outputs.latest_tag }}{% endraw %}"
          version=${latest_tag#v}
          IFS='.' read -r major minor patch <<< "$version"

          release_type="{% raw %}${{ github.event.inputs.release_type }}{% endraw %}"

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

      - name: Create tag locally (do not push yet)
        run: |
          new_version="{% raw %}${{ steps.calc_version.outputs.new_version }}{% endraw %}"

          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

          git tag -a "$new_version" -m "Release $new_version"

          echo "✅ Created local tag: $new_version"
          echo "   (Tag will be pushed only if build and tests succeed)"

      - name: Debug git state for version detection
        run: |
          echo "=== Git Describe Output ==="
          git describe --tags --long --dirty --always
          echo ""
          echo "=== Current HEAD ==="
          git rev-parse HEAD
          echo ""
          echo "=== Tags at HEAD ==="
          git tag --points-at HEAD

      - name: Set up Python {{ python_version }}
        uses: actions/setup-python@v4
        with:
          python-version: '{{ python_version }}'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests with pytest
        run: python -m pytest {{ test_path }}

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          verbose: {{ verbose_publish | lower }}

      - name: Push tag to remote
        run: |
          new_version="{% raw %}${{ steps.calc_version.outputs.new_version }}{% endraw %}"
          git push origin "$new_version"
          echo "✅ Pushed tag to remote: $new_version"
        env:
          GITHUB_TOKEN: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}

      - name: Create GitHub Release
        run: |
          new_version="{% raw %}${{ steps.calc_version.outputs.new_version }}{% endraw %}"
          gh release create "$new_version" \
            --title "Release $new_version" \
            --generate-notes
        env:
          GITHUB_TOKEN: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}

      - name: Summary
        run: |
          new_version="{% raw %}${{ steps.calc_version.outputs.new_version }}{% endraw %}"
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

**Key Design Decisions:**
- ✅ **Single job** - All steps in one job for correct ordering
- ✅ **Tag created locally first** - setuptools_scm can detect it for version
- ✅ **Test/build before push** - Tag only pushed if all steps succeed
- ✅ **Automatic cleanup** - If any step fails, local tag is discarded with the runner
- ✅ **Remote tag check** - Uses `git ls-remote` to check if tag exists on origin
- ✅ **Clear progress messages** - Users can see exactly what's happening
- ✅ **Uses default GITHUB_TOKEN** - No PAT required!
- ✅ **Summary output** - GitHub Actions summary shows what was accomplished

**Why not use reusable workflow here:**
- Release workflow needs special ordering (tag locally → test → push tag)
- Each GitHub Actions job gets a fresh runner, so local tags don't persist across jobs
- Simpler to inline the build/test/publish steps for this special case
- PR testing still benefits from reusable workflow pattern

### 3. PR Testing Workflow: test-pr.yml

**Purpose:** Run tests and publish to TestPyPI for pull requests.

**Trigger:** `pull_request` to main branch

**Implementation:**

```yaml
name: Test and Publish to TestPyPI

on:
  pull_request:
    branches: [ main ]

jobs:
  test-and-publish:
    uses: ./.github/workflows/_reusable-build-publish.yml
    permissions:
      id-token: write  # For TestPyPI Trusted Publishing
      contents: read
    with:
      publish_target: 'testpypi'
    secrets: inherit
```

**Key Design Decisions:**
- ✅ **Minimal workflow** - Just calls reusable workflow
- ✅ **No duplication** - All logic in reusable workflow
- ✅ **Clear intent** - Workflow name makes purpose obvious

## Template File Structure

### Generator Template Files

```
pypi_workflow_generator/
├── _reusable_build_publish.yml.j2  # Reusable workflow template (for PR testing)
├── release.yml.j2                   # Release workflow (inline build/test/publish)
├── test_pr.yml.j2                   # PR testing workflow (calls reusable)
├── create_release.yml.j2            # DELETE: Replaced by release.yml.j2
└── pypi_publish.yml.j2              # DELETE: Replaced by test_pr.yml.j2 + _reusable_build_publish.yml.j2
```

### Generated Files

```
.github/workflows/
├── _reusable-build-publish.yml  # Core build/test/publish logic (called by test-pr.yml)
├── release.yml                   # Manual release (inline, special ordering)
└── test-pr.yml                   # PR testing (calls reusable workflow)
```

## Implementation Plan

### Phase 1: Create New Templates (Preparation)

**Effort:** 2-3 hours

1. **Create `_reusable_build_publish.yml.j2`**
   - Extract test/build/publish logic from current `pypi_publish.yml.j2`
   - Add `workflow_call` trigger with inputs
   - Parameterize publish target
   - Add git ref input for checkout
   - Test with various input combinations

2. **Create `release.yml.j2`**
   - Copy version calculation logic from `create_release.yml.j2`
   - Add tag existence check
   - Add tag creation and push (using GITHUB_TOKEN)
   - Add GitHub Release creation
   - Add job that calls reusable workflow
   - Pass new version tag as `ref` input

3. **Create `test_pr.yml.j2`**
   - Simple workflow that calls reusable workflow
   - Set `publish_target: 'testpypi'`
   - Minimal configuration

### Phase 2: Update Generator Logic

**Effort:** 2-3 hours

1. **Update `generator.py`**

   **Current:**
   ```python
   def generate_workflow(
       package_name: str,
       python_version: str = '3.11',
       test_path: str = 'tests/',
       output_filename: str = 'pypi-publish.yml',
       base_output_dir: Optional[str] = None,
       verbose_publish: bool = True,
       release_on_main_push: bool = False
   ) -> Dict[str, Any]:
   ```

   **New:**
   ```python
   def generate_workflows(
       package_name: str,
       python_version: str = '3.11',
       test_path: str = 'tests/',
       base_output_dir: Optional[str] = None,
       verbose_publish: bool = True
   ) -> Dict[str, Any]:
       """
       Generate GitHub Actions workflows for PyPI publishing.

       Generates 3 files:
           - _reusable-build-publish.yml (shared build/test/publish logic)
           - release.yml (manual releases via GitHub UI)
           - test-pr.yml (PR testing to TestPyPI)

       Returns:
           Dict with:
               - success: bool
               - files_created: List[str]
               - message: str
       """
       # Generate _reusable-build-publish.yml
       # Generate release.yml
       # Generate test-pr.yml
   ```

2. **Remove old parameters:**
   - `output_filename` - No longer needed (generate all 3 files with fixed names)
   - `release_on_main_push` - No longer relevant (tag-based triggering removed)

3. **Delete old workflow generation functions:**
   - Remove `generate_pypi_publish_workflow()` (replaced by new templates)
   - Remove `generate_release_workflow()` (replaced by new template)

### Phase 3: Update CLI

**Effort:** 1-2 hours

1. **Update `main.py`**

   **Remove deprecated flags:**
   ```python
   # DELETE these arguments:
   # --output-filename (always generate 3 files with fixed names)
   # --release-on-main-push (no longer relevant)
   # --skip-release-workflow (always generate both workflows)
   ```

   **Keep existing flags:**
   ```python
   # These remain unchanged:
   # --package-name (required)
   # --python-version (default: 3.11)
   # --test-path (default: tests/)
   # --project-root (base directory)
   # --verbose-publish (default: True)
   ```

2. **Update help text:**
   ```python
   parser.description = """
   Generate GitHub Actions workflows for automated PyPI publishing.

   Generates 3 workflow files:
     - _reusable-build-publish.yml (shared build/test/publish logic)
     - release.yml (manual releases via GitHub UI)
     - test-pr.yml (PR testing to TestPyPI)

   Benefits:
     - No PAT or GitHub App tokens required
     - Test/build before pushing tags (safe failure handling)
     - DRY: shared logic for build/test/publish
     - Simple per-repository setup (only PyPI Trusted Publisher needed)

   Example:
     pypi-workflow-generator --package-name mypackage

   This creates:
     .github/workflows/_reusable-build-publish.yml
     .github/workflows/release.yml
     .github/workflows/test-pr.yml
   """
   ```

3. **Update function calls:**
   ```python
   # In main():
   result = generate_workflows(
       package_name=args.package_name,
       python_version=args.python_version,
       test_path=args.test_path,
       base_output_dir=workflows_dir,
       verbose_publish=args.verbose_publish
   )
   ```

### Phase 4: Update Documentation

**Effort:** 2-3 hours

1. **Update README.md**

   **Add prominent section at top:**
   ```markdown
   ## Quick Start (No PAT Required!)

   The default workflow pattern requires zero authentication setup beyond PyPI Trusted Publishing:

   1. Generate workflows:
      ```bash
      pypi-workflow-generator --package-name mypackage
      ```

   2. Set up PyPI Trusted Publisher (one-time):
      - [PyPI instructions](...)
      - [TestPyPI instructions](...)

   3. Create release via GitHub UI:
      - Actions → "Release to PyPI" → Run workflow
      - Select version bump type (patch/minor/major)
      - Done!
   ```

   **Remove PAT documentation:**
   - Delete or archive old PAT setup instructions
   - Remove references to RELEASE_PAT secret
   - Clean up workflow trigger documentation

2. **Create new guide: `docs/WORKFLOW_ARCHITECTURE.md`**
   - Explain the workflow pattern
   - Architecture diagram showing tag-local-first approach
   - How to customize workflows
   - Troubleshooting common issues

3. **Update `MCP-USAGE.md`**
   - Update examples to use new pattern
   - Remove PAT-related instructions
   - Add examples of workflow usage

### Phase 5: Update Tests

**Effort:** 2-3 hours

1. **Create `test_reusable_workflows.py`**
   ```python
   def test_generate_reusable_workflows(tmp_path: Path):
       """Test generation of all 3 reusable workflow files."""
       result = generate_reusable_workflows(
           package_name='test-package',
           base_output_dir=str(tmp_path)
       )

       assert result['success']
       assert len(result['files_created']) == 3

       # Check files exist
       assert (tmp_path / '_reusable-build-publish.yml').exists()
       assert (tmp_path / 'release.yml').exists()
       assert (tmp_path / 'test-pr.yml').exists()

   def test_reusable_workflow_has_workflow_call_trigger(tmp_path: Path):
       """Ensure reusable workflow has correct trigger."""
       generate_reusable_workflows(
           package_name='test-package',
           base_output_dir=str(tmp_path)
       )

       content = (tmp_path / '_reusable-build-publish.yml').read_text()
       assert 'workflow_call:' in content
       assert 'publish_target:' in content

   def test_release_workflow_calls_reusable(tmp_path: Path):
       """Ensure release workflow calls the reusable workflow."""
       generate_reusable_workflows(
           package_name='test-package',
           base_output_dir=str(tmp_path)
       )

       content = (tmp_path / 'release.yml').read_text()
       assert 'uses: ./.github/workflows/_reusable-build-publish.yml' in content
       assert "publish_target: 'pypi'" in content

   def test_tag_existence_check(tmp_path: Path):
       """Ensure release workflow checks if tag already exists."""
       generate_reusable_workflows(
           package_name='test-package',
           base_output_dir=str(tmp_path)
       )

       content = (tmp_path / 'release.yml').read_text()
       assert 'git rev-parse' in content
       assert 'Tag $new_version already exists' in content
   ```

2. **Update integration tests**
   - Test full workflow with reusable pattern
   - Verify YAML syntax validity
   - Test with different configurations

3. **Add CLI tests**
   ```python
   def test_cli_generates_all_workflows():
       """Ensure CLI generates all 3 workflow files."""
       result = subprocess.run([
           'pypi-workflow-generator',
           '--package-name', 'test-pkg',
           '--project-root', str(tmp_path)
       ], capture_output=True)

       assert (tmp_path / '.github/workflows/_reusable-build-publish.yml').exists()
       assert (tmp_path / '.github/workflows/release.yml').exists()
       assert (tmp_path / '.github/workflows/test-pr.yml').exists()

   def test_generated_workflows_valid_yaml():
       """Ensure generated workflows are valid YAML."""
       result = subprocess.run([
           'pypi-workflow-generator',
           '--package-name', 'test-pkg',
           '--project-root', str(tmp_path)
       ], capture_output=True)

       import yaml
       for workflow_file in ['_reusable-build-publish.yml', 'release.yml', 'test-pr.yml']:
           path = tmp_path / '.github/workflows' / workflow_file
           with open(path) as f:
               yaml.safe_load(f)  # Should not raise
   ```

### Phase 6: Dogfooding

**Effort:** 1-2 hours

1. **Backup existing workflows**
   ```bash
   mkdir -p .github/workflows.bak
   mv .github/workflows/create-release.yml .github/workflows.bak/
   mv .github/workflows/pypi-publish.yml .github/workflows.bak/
   ```

2. **Generate new workflows**
   ```bash
   python -m pypi_workflow_generator.main \
     --package-name pypi-workflow-generator \
     --project-root .
   ```

3. **Verify generated files**
   ```bash
   ls -la .github/workflows/
   # Should see:
   # _reusable-build-publish.yml
   # release.yml
   # test-pr.yml
   ```

4. **Delete RELEASE_PAT secret (no longer needed)**
   - Go to Settings → Secrets and variables → Actions
   - Delete `RELEASE_PAT` secret

5. **Test the new workflows**
   - Create a test PR → verify TestPyPI publish
   - Run "Release to PyPI" manually → verify production publish
   - Check that version detection works correctly
   - Verify tag is created AFTER build succeeds
   - Verify GitHub Release creation

6. **Delete backup if successful**
   ```bash
   rm -rf .github/workflows.bak
   ```

4. **Document findings**
   - Any issues encountered
   - Improvements needed
   - User experience notes

### Phase 7: Release and Communication

**Effort:** 1-2 hours

1. **Update CHANGELOG.md**
   ```markdown
   ## [0.3.0] - 2025-11-XX

   ### Added
   - Safe tag creation: tags now created locally and only pushed after tests/build succeed
   - Tag existence checking prevents duplicate releases
   - Reusable workflow pattern for PR testing
   - Comprehensive workflow execution summary

   ### Changed
   - **BREAKING**: Completely redesigned workflow architecture
   - No longer requires PAT or GitHub App tokens - uses default GITHUB_TOKEN
   - Release workflow now inline (test/build before tag push)
   - Removed `--output-filename` and `--release-on-main-push` CLI flags
   - Removed `--skip-release-workflow` flag (always generate all workflows)

   ### Removed
   - PAT-based workflow triggering (no longer needed)
   - Tag-based publish triggering (use GitHub UI instead)
   - Two-workflow pattern (replaced with new architecture)

   ### Migration from v0.2.x
   1. Backup existing workflows
   2. Regenerate using `pypi-workflow-generator --package-name <name>`
   3. Delete RELEASE_PAT secret (no longer needed)
   4. Test new workflows with a PR and release
   ```

2. **Create release**
   - Use the new release workflow to dogfood it!
   - Version bump: 0.2.x → 0.3.0 (minor version, new feature)

3. **Update PyPI description**
   - Highlight "no PAT required" in description
   - Update example usage

4. **Communicate changes**
   - GitHub release notes
   - Update any external documentation
   - Consider blog post if this is a significant improvement

## Comparison: Before vs After

### Before (Legacy Pattern)

**Files:**
- `create-release.yml` (50 lines)
- `pypi-publish.yml` (76 lines)
- **Total:** 126 lines across 2 files

**Setup Required:**
1. Configure PyPI Trusted Publisher
2. Configure TestPyPI Trusted Publisher
3. Create PAT with `repo` scope
4. Add `RELEASE_PAT` secret to repository

**Usage:**
- Actions → "Create Release" → Select version → Creates tag → Triggers publish

**Pros:**
- Can manually push tags to trigger publish
- Flexible (separate tag creation from publishing)

**Cons:**
- Requires PAT setup per repository
- PAT needs annual rotation
- More complex to understand (workflow chaining)
- Two files to maintain

### After (New Pattern)

**Files:**
- `_reusable-build-publish.yml` (~65 lines, for PR testing)
- `release.yml` (~100 lines, inline build/test/publish)
- `test-pr.yml` (~10 lines, calls reusable)
- **Total:** ~175 lines across 3 files

**Setup Required:**
1. Configure PyPI Trusted Publisher
2. Configure TestPyPI Trusted Publisher
3. ✅ **No PAT required!**

**Usage:**
- Actions → "Release to PyPI" → Select version → Tests/builds → Publishes to PyPI

**Pros:**
- ✅ **No PAT setup required** - Zero additional secrets
- ✅ **No token rotation** - Uses default GITHUB_TOKEN
- ✅ **Safe tag creation** - Tags only pushed if tests/build succeed
- ✅ **Tag existence checking** - Prevents duplicate tags
- ✅ **Simpler per-repo setup** - Only PyPI Trusted Publisher
- ✅ **Easier debugging** - Linear workflow execution
- ✅ **DRY for PR testing** - Reusable workflow pattern

**Cons:**
- ❌ Can't manually push tags to trigger publish (must use GitHub UI)
- ⚠️ Release workflow doesn't use reusable pattern (special ordering required)

**Key Improvement:**
- Tag creation now happens AFTER tests pass, preventing orphaned tags for failed releases

## Advanced: Optional Enhancements

### Enhancement 1: Local Release Script Support

**Problem:** Can't trigger release from CLI with new pattern.

**Solution:** Update `create_release.py` to use GitHub API:

```python
def create_release_via_api(
    release_type: str,
    token: Optional[str] = None
) -> None:
    """
    Trigger the 'Release to PyPI' workflow via GitHub API.

    This allows local release creation without PAT.
    Uses user's GitHub CLI authentication or provided token.
    """
    import subprocess

    # Use gh CLI to trigger workflow
    result = subprocess.run([
        'gh', 'workflow', 'run', 'release.yml',
        '-f', f'release_type={release_type}'
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error triggering workflow: {result.stderr}")
        sys.exit(1)

    print(f"✅ Release workflow triggered for {release_type} version bump")
    print("View progress: gh run watch")
```

**Benefit:** Maintains CLI workflow option for developers who prefer it.

### Enhancement 2: Release from Branch

**Problem:** All releases come from main branch.

**Solution:** Add branch input to release workflow:

```yaml
on:
  workflow_dispatch:
    inputs:
      release_type:
        # ... existing
      branch:
        description: 'Branch to release from (default: main)'
        required: false
        type: string
        default: 'main'
```

**Benefit:** Supports hotfix releases from release branches.

### Enhancement 3: Dry Run Mode

**Problem:** Can't test release process without actually releasing.

**Solution:** Add dry-run input:

```yaml
inputs:
  dry_run:
    description: 'Dry run (create tag and test build, but do not publish or create GitHub Release)'
    required: false
    type: boolean
    default: false
```

Update reusable workflow:
```yaml
- name: Publish to PyPI
  if: inputs.publish_target == 'pypi' && !inputs.dry_run
  # ...
```

**Benefit:** Safe testing of release process.

### Enhancement 4: Automatic Changelog Generation

**Problem:** No changelog maintenance.

**Solution:** Add changelog generation step using GitHub's auto-generated release notes:

```yaml
- name: Generate changelog
  run: |
    gh api repos/${{ github.repository }}/releases/generate-notes \
      -f tag_name="${{ steps.calc_version.outputs.new_version }}" \
      -f target_commitish=main \
      -q .body > CHANGELOG_ENTRY.md
```

**Benefit:** Automated release notes.

## Risks and Mitigations

### Risk 1: Breaking Change for Existing Users

**Impact:** Users with v0.2.x workflows will need to regenerate workflows.

**Mitigation:**
- Clear CHANGELOG marking this as a breaking change
- Simple migration steps documented
- Emphasize benefits: no PAT setup, safer releases
- Version bump to 0.3.0 signals breaking change

### Risk 2: Loss of Tag-Based Triggering

**Impact:** Users who manually push tags can't trigger publish anymore.

**Mitigation:**
- Document this clearly as a trade-off
- Most users release via UI anyway
- Offer Enhancement 1 (CLI triggering via `gh workflow run`)
- Benefit (safe tag creation) outweighs this limitation

### Risk 3: Local Tag Creation Complexity

**Impact:** The "create local tag first" pattern may be unfamiliar.

**Mitigation:**
- Clear documentation with diagrams
- Debug output shows git state at each step
- Well-commented workflow steps
- Test thoroughly to ensure it works correctly

### Risk 4: Inline Release Workflow (Not Using Reusable Pattern)

**Impact:** Release workflow has duplicate build/test steps compared to reusable workflow.

**Mitigation:**
- Document why this is necessary (local tag persistence)
- The duplication is minimal and intentional
- PR testing still benefits from reusable pattern
- Trade-off is acceptable for correct behavior

## Success Criteria

### Must Have (MVP)
- ✅ Generate 3 workflow files
- ✅ Zero PAT requirement
- ✅ Tags only pushed after successful build/test
- ✅ All tests pass
- ✅ Dogfooded successfully on this project
- ✅ Documentation updated

### Should Have
- ✅ Tag existence checking prevents duplicates
- ✅ Clear error messages for common issues
- ✅ Integration tests cover new pattern
- ✅ Migration guide for v0.2.x users

### Nice to Have
- ⚠️ Video walkthrough of new pattern
- ⚠️ Local release CLI support (Enhancement 1)
- ⚠️ Dry run mode (Enhancement 3)

## Timeline Estimate

| Phase | Effort | Duration |
|-------|--------|----------|
| Phase 1: Create Templates | 2-3 hours | 1 day |
| Phase 2: Update Generator | 2-3 hours | 1 day |
| Phase 3: Update CLI | 1-2 hours | 0.5 days |
| Phase 4: Documentation | 2-3 hours | 1 day |
| Phase 5: Tests | 2-3 hours | 1 day |
| Phase 6: Dogfooding | 1-2 hours | 0.5 days |
| Phase 7: Release | 1-2 hours | 0.5 days |
| **Total** | **11-18 hours** | **5-6 days** |

**Note:** Can be parallelized or done incrementally.

## Implementation Order (Recommended)

1. **Phase 1** (Templates) - Foundation
2. **Phase 5** (Tests) - TDD approach, write tests first
3. **Phase 2** (Generator) - Implement to make tests pass
4. **Phase 3** (CLI) - Wire everything together
5. **Phase 6** (Dogfooding) - Real-world validation
6. **Phase 4** (Documentation) - Document what works
7. **Phase 7** (Release) - Ship it!

## Open Questions

1. **Should we add more publish targets?**
   - Current: 'pypi', 'testpypi', 'none'
   - Future: 'artifactory', 'aws-codeartifact', etc.?
   - **Decision:** Keep simple for v0.3.0, users can customize reusable workflow if needed

2. **Should we support custom test commands?**
   - Currently hardcoded: `python -m pytest {{ test_path }}`
   - Could add `--test-command` flag for flexibility
   - **Decision:** Add if users request it, start simple

3. **Should we generate .github/workflows directory if it doesn't exist?**
   - **Decision:** Yes, create it automatically with appropriate messaging

## Conclusion

This plan consolidates the two-workflow architecture into a simpler, more maintainable pattern. The key benefits are:

1. **Zero PAT requirement** - Eliminates per-repo setup burden (only PyPI Trusted Publisher needed)
2. **Safe tag creation** - Tags only pushed after tests/build succeed, preventing orphaned tags
3. **DRY for PR testing** - Reusable workflow pattern for test-pr.yml
4. **Simpler architecture** - No workflow chaining, linear execution
5. **Better user experience** - Clear error messages, progress indicators

The trade-off (loss of tag-based triggering) is acceptable given the significant reduction in setup complexity and improved safety.

**Recommendation:** Proceed with implementation using the phased approach outlined above, starting with templates and tests.
