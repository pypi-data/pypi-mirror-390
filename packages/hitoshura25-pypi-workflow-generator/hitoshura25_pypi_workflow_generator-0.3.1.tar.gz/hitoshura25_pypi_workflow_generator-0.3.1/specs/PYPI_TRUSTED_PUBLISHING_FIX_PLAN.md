# IMPLEMENTATION PLAN: Fix PyPI Trusted Publishing with Reusable Workflows

**Date:** 2025-11-05
**Issue:** PyPI Trusted Publishing doesn't support reusable workflows
**Solution:** Extract publishing steps from reusable workflow, pass artifacts between jobs

---

## Problem Statement

The current implementation uses a reusable workflow (`_reusable-build-publish.yml`) that performs test → build → publish. When called by `test-pr.yml`, PyPI's Trusted Publishing sees:
- `workflow_ref`: `test-pr.yml` (the caller)
- `job_workflow_ref`: `_reusable-build-publish.yml` (where publish actually runs)

PyPI validates against `workflow_ref` but the publish action runs in `job_workflow_ref`, causing authentication failure. PyPI does not currently support reusable workflows for Trusted Publishing.

**Error Message:**
```
Reusable workflows are **not currently supported** by PyPI's Trusted Publishing
Token request failed: the server refused the request for the following reasons:
* `invalid-publisher`: valid token, but no corresponding publisher
```

**References:**
- https://docs.pypi.org/trusted-publishers/troubleshooting/#reusable-workflows-on-github
- https://github.com/pypa/gh-action-pypi-publish/issues/166

---

## Solution Architecture

### Current (Broken):
```
test-pr.yml
  └─ calls _reusable-build-publish.yml
       └─ test → build → publish ❌ (PyPI rejects: wrong workflow_ref)
```

### New (Fixed):
```
test-pr.yml
  ├─ Job 1: calls _reusable-test-build.yml
  │    └─ test → build → upload-artifact
  └─ Job 2 (inline): download-artifact → publish ✅ (PyPI accepts: correct workflow_ref)
```

**Key Insight:** The publish step must run directly in `test-pr.yml` or `release.yml`, but test/build can be in a reusable workflow. Artifacts are passed between jobs using GitHub Actions' native artifact system.

---

## Phase 1: Update Workflow Templates

### 1.1 Rename and Update: `_reusable_build_publish.yml.j2` → `_reusable_test_build.yml.j2`

**Changes:**
1. **Rename file**
2. **Remove `publish_target` input parameter** (no longer publishes)
3. **Remove both publish steps** (TestPyPI and PyPI publish actions)
4. **Add artifact upload step**:
   ```yaml
   - name: Store the distribution packages
     uses: actions/upload-artifact@v4
     with:
       name: python-package-distributions
       path: dist/
   ```
5. **Update permissions** (only needs `contents: read`, remove `id-token: write`)
6. **Update name**: "Reusable Test and Build" (not "Build and Publish")

**Complete Template Structure:**
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
      ref:
        description: 'Git ref to checkout (tag, branch, or commit)'
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
          echo "=== Tags at HEAD ==="
          git tag --points-at HEAD

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
        run: python -m build

      - name: Store the distribution packages
        uses: actions/upload-artifact@v4
        with:
          name: python-package-distributions
          path: dist/
```

### 1.2 Update: `test_pr.yml.j2`

**Changes:**
1. **Convert from single reusable call to two-job structure**
2. **Job 1**: Call `_reusable-test-build.yml` reusable workflow
3. **Job 2**: Inline publish to TestPyPI

**Complete Template Structure:**
```yaml
name: Test and Publish to TestPyPI

on:
  pull_request:
    branches: [ main ]

jobs:
  test-and-build:
    uses: ./.github/workflows/_reusable-test-build.yml
    with:
      python_version: '{{ python_version }}'
      test_path: '{{ test_path }}'

  publish-to-testpypi:
    name: Publish to TestPyPI
    needs: [test-and-build]
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

**Key Points:**
- `needs: [test-and-build]` ensures sequential execution
- `id-token: write` only on publish job (where it's needed)
- Artifact name must match between upload and download: `python-package-distributions`
- Path `dist/` must be consistent

### 1.3 Update: `release.yml.j2`

**Changes:**
1. **Job 1**: Keep existing tag creation logic (unchanged)
2. **Job 2**: Call `_reusable-test-build.yml` instead of inline build
3. **Job 3**: New inline publish job with artifact download

**Complete Template Structure:**
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
  create-tag:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    outputs:
      new_version: {% raw %}${{ steps.calc_version.outputs.new_version }}{% endraw %}

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

  test-and-build:
    needs: [create-tag]
    uses: ./.github/workflows/_reusable-test-build.yml
    with:
      python_version: '{{ python_version }}'
      test_path: '{{ test_path }}'
      ref: {% raw %}${{ needs.create-tag.outputs.new_version }}{% endraw %}

  publish-to-pypi:
    name: Publish to PyPI
    needs: [create-tag, test-and-build]
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

      - name: Push tag to remote
        run: |
          new_version="{% raw %}${{ needs.create-tag.outputs.new_version }}{% endraw %}"
          git fetch --tags
          git push origin "$new_version"
          echo "✅ Pushed tag to remote: $new_version"
        env:
          GITHUB_TOKEN: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}

      - name: Create GitHub Release
        run: |
          new_version="{% raw %}${{ needs.create-tag.outputs.new_version }}{% endraw %}"
          gh release create "$new_version" \
            --title "Release $new_version" \
            --generate-notes
        env:
          GITHUB_TOKEN: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}

      - name: Summary
        run: |
          new_version="{% raw %}${{ needs.create-tag.outputs.new_version }}{% endraw %}"
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

**Key Points:**
- Three-job chain: `create-tag` → `test-and-build` → `publish-to-pypi`
- Tag only pushed after successful publish (safe tag creation preserved)
- Checkout needed in publish job for git commands (push tag, create release)
- `needs.create-tag.outputs.new_version` passed to build job via `ref` input

---

## Phase 2: Update Generator Logic

### 2.1 Update: `generator.py`

**File:** `pypi_workflow_generator/generator.py`

**Changes in `generate_workflows()` function:**

Around line ~71-75, update the `workflow_templates` list:

```python
# Old:
workflow_templates = [
    ('_reusable_build_publish.yml.j2', '_reusable-build-publish.yml'),
    ('release.yml.j2', 'release.yml'),
    ('test_pr.yml.j2', 'test-pr.yml')
]

# New:
workflow_templates = [
    ('_reusable_test_build.yml.j2', '_reusable-test-build.yml'),  # CHANGED: renamed
    ('release.yml.j2', 'release.yml'),
    ('test_pr.yml.j2', 'test-pr.yml')
]
```

**That's the only change needed in generator.py** - just update the template filename.

---

## Phase 3: Update Tests

### 3.1 Update: `test_server.py`

**File:** `pypi_workflow_generator/tests/test_server.py`

**Changes in multiple test functions:**

Replace all instances of:
```python
reusable_path = tmp_path / ".github" / "workflows" / "_reusable-build-publish.yml"
```

With:
```python
reusable_path = tmp_path / ".github" / "workflows" / "_reusable-test-build.yml"
```

**Affected functions:**
- `test_call_tool_generate_workflows()` (around line ~88)
- `test_call_tool_generate_workflows_with_options()` (around line ~130)
- `test_generate_workflows_creates_all_files_via_mcp()` (around line ~323)

### 3.2 Update: `test_generator.py`

**File:** `pypi_workflow_generator/tests/test_generator.py`

**Changes in test functions:**

Replace all instances of:
```python
reusable_file = output_dir / '_reusable-build-publish.yml'
```

With:
```python
reusable_file = output_dir / '_reusable-test-build.yml'
```

**Affected functions:**
- `test_generate_workflows_default_arguments()` (around line ~28)
- `test_generate_workflows_custom_arguments()` (around line ~71)

### 3.3 Update: `test_release_workflow.py`

**File:** `pypi_workflow_generator/tests/test_release_workflow.py`

**Changes in test functions:**

Replace all instances of:
```python
assert (output_dir / '_reusable-build-publish.yml').exists()
```

With:
```python
assert (output_dir / '_reusable-test-build.yml').exists()
```

**Affected function:**
- `test_generate_workflows_includes_all_three_files()` (around line ~93)

---

## Phase 4: Update Documentation

### 4.1 Update: `README.md`

#### Section: Generated Workflows (around line ~122)

Replace the reusable workflow description with:

```markdown
### 3. Reusable Test and Build Workflow (`_reusable-test-build.yml`)

Shared logic called by other workflows:

- **Parameterized**: Accepts Python version, test path, and git ref
- **Test Pipeline**: Checkout → setup → test → build
- **Artifact Export**: Uploads built packages for use by caller workflows
- **Reusable**: Single source of truth for test/build logic
- **Note**: Does NOT publish (publishing done by caller workflows for PyPI Trusted Publishing compatibility)
```

#### Section: Setting Up Trusted Publishers (around line ~204)

Update the workflow name instructions:

```markdown
3. **Add Trusted Publishers:**
   - You need to add **two** publishers (one for production, one for testing)
   - Click on the "Add a new publisher" button.
   - Select "GitHub Actions" as the publisher type.
   - For **PyPI** (production releases):
     - **Owner:** Your GitHub username or organization (e.g., `your-username`)
     - **Repository:** Your repository name (e.g., `my-awesome-package`)
     - **Workflow Name:** `release.yml`
     - **Environment (Optional):** Leave blank
   - For **TestPyPI** (PR testing):
     - **Owner:** Same as above
     - **Repository:** Same as above
     - **Workflow Name:** `test-pr.yml`
     - **Environment (Optional):** Leave blank

   **Important:** Do NOT use `_reusable-test-build.yml` as the workflow name. PyPI Trusted Publishing does not support reusable workflows. The workflow name must be the file that contains the publish step (`test-pr.yml` or `release.yml`).
```

#### Section: Features (around line ~5-16)

Add a new feature bullet:

```markdown
- ✅ **Trusted Publishing Compatible**: Works around PyPI's reusable workflow limitation
```

#### Section: Dogfooding (around line ~346)

Update the workflow file list:

```markdown
This project uses itself to generate its own GitHub Actions workflows! The workflow files at:
- `.github/workflows/_reusable-test-build.yml`
- `.github/workflows/release.yml`
- `.github/workflows/test-pr.yml`

Were all created by running:

```bash
pypi-workflow-generator \
  --package-name pypi-workflow-generator \
  --python-version 3.11 \
  --test-path pypi_workflow_generator/ \
  --verbose-publish
```
```

---

## Phase 5: Re-Dogfood on This Project

### 5.1 Regenerate Workflows

**Steps:**

1. **Install updated package:**
   ```bash
   pip install -e .
   ```

2. **Run generator:**
   ```bash
   pypi-workflow-generator \
     --package-name pypi-workflow-generator \
     --python-version 3.11 \
     --test-path pypi_workflow_generator/ \
     --verbose-publish
   ```

3. **Remove old file:**
   ```bash
   rm .github/workflows/_reusable-build-publish.yml
   ```

4. **Verify new files created:**
   - `.github/workflows/_reusable-test-build.yml` ✅
   - `.github/workflows/release.yml` ✅
   - `.github/workflows/test-pr.yml` ✅

---

## Phase 6: Testing and Validation

### 6.1 Run All Tests

```bash
pytest pypi_workflow_generator/tests/ -v
```

**Expected:** All 19 tests pass ✅

### 6.2 Validate Generated Workflows

**Check `_reusable-test-build.yml`:**
- ✅ Has `upload-artifact@v4` step
- ✅ Does NOT have any `pypa/gh-action-pypi-publish` steps
- ✅ Has `contents: read` permission only
- ✅ Has all test and build steps

**Check `test-pr.yml`:**
- ✅ Has two jobs: `test-and-build` and `publish-to-testpypi`
- ✅ Uses `./.github/workflows/_reusable-test-build.yml`
- ✅ Has `needs: [test-and-build]` in publish job
- ✅ Has `download-artifact@v4` in publish job
- ✅ Has `pypa/gh-action-pypi-publish` in publish job
- ✅ Publish job has `id-token: write` permission

**Check `release.yml`:**
- ✅ Has three jobs: `create-tag`, `test-and-build`, `publish-to-pypi`
- ✅ Uses `./.github/workflows/_reusable-test-build.yml`
- ✅ Has `needs: [create-tag, test-and-build]` in publish job
- ✅ Has `download-artifact@v4` in publish job
- ✅ Has `pypa/gh-action-pypi-publish` in publish job
- ✅ Tag only pushed after successful publish
- ✅ Publish job has both `id-token: write` and `contents: write` permissions

---

## Summary of Changes

### Files Modified (8):
1. `pypi_workflow_generator/_reusable_build_publish.yml.j2` → **RENAME to** `_reusable_test_build.yml.j2` + modify
2. `pypi_workflow_generator/test_pr.yml.j2` - rewrite to two-job structure
3. `pypi_workflow_generator/release.yml.j2` - rewrite to three-job structure with artifact passing
4. `pypi_workflow_generator/generator.py` - update template filename
5. `pypi_workflow_generator/tests/test_server.py` - update filename assertions (3 functions)
6. `pypi_workflow_generator/tests/test_generator.py` - update filename assertions (2 functions)
7. `pypi_workflow_generator/tests/test_release_workflow.py` - update filename assertions (1 function)
8. `README.md` - update documentation (4 sections)

### Files Deleted (1):
1. `.github/workflows/_reusable-build-publish.yml` - replaced by `_reusable-test-build.yml`

### Files Created (1):
1. `.github/workflows/_reusable-test-build.yml` - new generated workflow

---

## Why This Works

### PyPI's Validation:
- PyPI checks the `workflow` claim in the OIDC token
- When publish runs in `test-pr.yml` directly, the `workflow` claim is `test-pr.yml`
- This matches the Trusted Publisher configuration → ✅ Authentication succeeds

### Artifact Passing:
- GitHub Actions artifacts are stored between jobs automatically
- `upload-artifact@v4` in Job 1 → `download-artifact@v4` in Job 2
- Built packages (`dist/`) are available for publishing
- No special configuration needed
- Artifact name: `python-package-distributions` (standard convention)

### Safe Tag Creation Preserved:
- Tags still created locally first in `create-tag` job
- Tests and build run in `test-and-build` job
- Publish runs in `publish-to-pypi` job
- Tag only pushed after all jobs succeed
- If any job fails, the tag is never pushed to remote

### DRY Maintained:
- Test and build logic still shared via `_reusable-test-build.yml`
- Only publish steps are duplicated (but they're simple: download + publish action)
- Better than fully inlining everything in both workflows
- Easier to maintain than duplicate test/build logic

---

## Technical Details

### Artifact Upload/Download Pattern

**Upload (in `_reusable-test-build.yml`):**
```yaml
- name: Store the distribution packages
  uses: actions/upload-artifact@v4
  with:
    name: python-package-distributions  # Standard name
    path: dist/                          # Where build outputs go
```

**Download (in caller workflows):**
```yaml
- name: Download all the dists
  uses: actions/download-artifact@v4
  with:
    name: python-package-distributions  # Must match upload
    path: dist/                          # Where publish expects them
```

### Job Dependency Chain

**For `test-pr.yml`:**
```
test-and-build → publish-to-testpypi
```

**For `release.yml`:**
```
create-tag → test-and-build → publish-to-pypi
```

### Permissions Matrix

| Job | contents | id-token | Why |
|-----|----------|----------|-----|
| test-and-build | read | - | Read code, no publish |
| publish-to-testpypi | - | write | Trusted Publishing auth |
| publish-to-pypi | write | write | Trusted Publishing + push tag/create release |

---

## Rollout Checklist

- [ ] **Phase 1:** Update all 3 workflow templates
  - [ ] Rename `_reusable_build_publish.yml.j2` → `_reusable_test_build.yml.j2`
  - [ ] Remove publish steps, add artifact upload
  - [ ] Update `test_pr.yml.j2` to two-job structure
  - [ ] Update `release.yml.j2` to three-job structure with artifact passing

- [ ] **Phase 2:** Update generator.py
  - [ ] Change template filename in `workflow_templates` list

- [ ] **Phase 3:** Update all test files
  - [ ] Update `test_server.py` (3 functions)
  - [ ] Update `test_generator.py` (2 functions)
  - [ ] Update `test_release_workflow.py` (1 function)

- [ ] **Phase 4:** Update README.md documentation
  - [ ] Update "Generated Workflows" section
  - [ ] Update "Setting Up Trusted Publishers" section
  - [ ] Add new feature bullet
  - [ ] Update "Dogfooding" section

- [ ] **Phase 5:** Re-dogfood (regenerate workflows for this project)
  - [ ] Run `pip install -e .`
  - [ ] Run `pypi-workflow-generator` command
  - [ ] Delete old `_reusable-build-publish.yml`
  - [ ] Verify 3 new files created

- [ ] **Phase 6:** Run tests and validate
  - [ ] Run `pytest pypi_workflow_generator/tests/ -v`
  - [ ] Verify all 19 tests pass
  - [ ] Manually inspect generated workflows

- [ ] **Git Commit:**
  - [ ] Stage all changes
  - [ ] Write descriptive commit message
  - [ ] Commit changes

- [ ] **PyPI Configuration:**
  - [ ] Update TestPyPI Trusted Publisher: workflow name = `test-pr.yml`
  - [ ] Update PyPI Trusted Publisher: workflow name = `release.yml`

- [ ] **Integration Testing:**
  - [ ] Create a test PR to verify TestPyPI publish works
  - [ ] Create a release to verify PyPI publish works
  - [ ] Verify tags are pushed correctly
  - [ ] Verify GitHub Releases are created

---

## Gotchas and Pitfalls

### 1. Artifact Version Compatibility 🚨
- Use `upload-artifact@v4` with `download-artifact@v4` or `v5`
- v3 is being deprecated (January 30, 2025)
- v4 is NOT backward compatible with v3
- Do NOT mix versions

### 2. Artifact Naming 🚨
- Must use exact same name in upload and download
- Standard name: `python-package-distributions`
- Case-sensitive

### 3. setuptools_scm Requirements 🚨
- Ensure `fetch-depth: 0` in checkout
- Ensure `fetch-tags: true` in checkout
- Tags must be present when building

### 4. Permissions 🚨
- Build job: Only `contents: read`
- Publish job: Must have `id-token: write`
- Release workflow publish job: Needs both `id-token: write` and `contents: write`

### 5. Job Dependencies 🚨
- Must use `needs:` to ensure correct ordering
- Without it, publish will fail (no artifacts)

### 6. PyPI Configuration 📝
- Configure with caller workflow names (`test-pr.yml`, `release.yml`)
- NOT the reusable workflow name (`_reusable-test-build.yml`)

### 7. Reusable Workflow Paths 📝
- Use relative path: `./.github/workflows/_reusable-test-build.yml`
- NOT absolute GitHub path

---

## Expected Outcomes

### After Implementation:

✅ **PyPI Trusted Publishing works** on both TestPyPI and PyPI
✅ **No PAT required** - uses default GITHUB_TOKEN
✅ **Safe tag creation preserved** - tags only pushed after successful publish
✅ **DRY architecture maintained** - shared test/build logic
✅ **All tests pass** - 19/19 tests passing
✅ **Works in production** - proven pattern used by other projects

### User Experience:

**For PRs:**
1. PR opened/updated
2. `test-pr.yml` runs
3. Tests pass, package builds
4. Publishes to TestPyPI automatically
5. Developer can test the pre-release version

**For Releases:**
1. Developer triggers "Release to PyPI" workflow via GitHub UI
2. Chooses patch/minor/major
3. Workflow creates tag locally
4. Tests pass, package builds
5. Publishes to PyPI
6. Tag pushed to remote
7. GitHub Release created
8. Users can install from PyPI

---

**END OF IMPLEMENTATION PLAN**

This plan maintains all the benefits of the original implementation while fixing the critical PyPI Trusted Publishing compatibility issue. The solution is officially recommended by PyPI and confirmed to work in production.
