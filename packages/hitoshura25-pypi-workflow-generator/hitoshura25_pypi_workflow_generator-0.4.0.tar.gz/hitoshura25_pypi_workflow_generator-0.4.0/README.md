# hitoshura25-pypi-workflow-generator

A dual-mode tool (MCP server + CLI) for generating GitHub Actions workflows for Python package publishing to PyPI.

## Features

- ✅ **Dual-Mode Operation**: Works as MCP server for AI agents OR traditional CLI for developers
- ✅ **PyPI Trusted Publishers**: Secure publishing without API tokens
- ✅ **No PAT Required**: Uses default GitHub token - zero additional setup
- ✅ **Safe Tag Creation**: Tags only pushed AFTER successful PyPI publish (fail-safe design)
- ✅ **Automated Versioning**: Uses setuptools_scm for git-based versioning
- ✅ **DRY Version Logic**: Shared script eliminates duplicate version calculation code
- ✅ **setuptools_scm Compatible**: Proper version detection in reusable workflows via SETUPTOOLS_SCM_PRETEND_VERSION
- ✅ **Pre-release Testing**: Automatic TestPyPI publishing on pull requests with PEP 440 development versions
- ✅ **Production Publishing**: Manual releases via GitHub Actions UI
- ✅ **Complete Project Initialization**: Generates pyproject.toml and setup.py
- ✅ **DRY Architecture**: Reusable workflows for shared logic

## Installation

```bash
pip install hitoshura25-pypi-workflow-generator
```

## Package Naming Best Practices

### Automatic Prefix Detection

By default, the generator adds your git username as a prefix to avoid PyPI naming conflicts. This follows PyPI best practices where package names should be unique and clearly identify the maintainer or organization.

**Example:**
```bash
# Your git config shows: github.com/jsmith/my-repo
$ hitoshura25-pypi-workflow-generator-init --package-name coolapp ...

# Auto-detects and creates:
# - PyPI Package: jsmith-coolapp
# - Import name: jsmith_coolapp
```

**Detection Priority:**
1. `git config --get github.user` (most specific)
2. GitHub username from remote URL (e.g., `git@github.com:username/repo.git`)
3. `git config --get user.name` (sanitized)

### Prefix Options

**Auto-detect (default)** - For personal projects:
```bash
hitoshura25-pypi-workflow-generator-init --package-name coolapp ...
# Creates: your-username-coolapp
```

**Custom Prefix** - For organization packages:
```bash
hitoshura25-pypi-workflow-generator-init --package-name coolapp --prefix acme ...
# Creates: acme-coolapp
```

**No Prefix** - For unique standalone tools:
```bash
hitoshura25-pypi-workflow-generator-init --package-name unique-name --no-prefix ...
# Creates: unique-name (check PyPI availability first!)
```

### Why Prefixes?

PyPI has a **flat namespace** - only ONE package globally can have a given name. Prefixes help:
- ✅ Avoid naming conflicts with existing packages
- ✅ Group related packages by maintainer/organization
- ✅ Make ownership clear (e.g., `acme-*` packages belong to Acme Corp)
- ✅ Enable unique names without creative spelling

### Configure Git (If Not Set)

```bash
# Set GitHub username (recommended)
git config --global github.user YOUR_GITHUB_USERNAME

# Or set git user.name (will be sanitized: "John Smith" → "john-smith")
git config --global user.name "Your Name"
```

## Usage

This package can be used in three ways:

### 1. MCP Mode (For AI Agents)

For AI agents with MCP support (Claude Code, Continue.dev, Cline):

**Add to `claude_desktop_config.json` or `claude_config.json`**:
```json
{
  "mcpServers": {
    "hitoshura25-pypi-workflow-generator": {
      "command": "mcp-hitoshura25-pypi-workflow-generator"
    }
  }
}
```

The agent can now use these tools:
- `generate_workflows` - Generate all 3 GitHub Actions workflows (no PAT required!)
- `initialize_project` - Create pyproject.toml and setup.py
- `create_release` - Create and push git release tags

**Example conversation**:
```
You: "Please set up a PyPI publishing workflow for my Python project"

Claude: I'll help you set up a complete PyPI publishing workflow.

[Calls initialize_project and generate_workflows tools]

✅ Created:
  - pyproject.toml
  - setup.py
  - .github/workflows/_reusable-test-build.yml
  - .github/workflows/release.yml
  - .github/workflows/test-pr.yml
  - scripts/calculate_version.sh

Next steps:
1. Configure Trusted Publishers on PyPI and TestPyPI
2. Create release via GitHub UI: Actions → "Release to PyPI"
```

### 2. CLI Mode (For Developers)

**Initialize a new project**:
```bash
hitoshura25-pypi-workflow-generator-init \
  --package-name my-awesome-package \
  --author "Your Name" \
  --author-email "your.email@example.com" \
  --description "My awesome Python package" \
  --url "https://github.com/username/my-awesome-package" \
  --command-name my-command
```

**Generate workflows**:
```bash
hitoshura25-pypi-workflow-generator
```

This creates 3 workflow files and 1 script:
- `.github/workflows/_reusable-test-build.yml` - Shared test/build logic
- `.github/workflows/release.yml` - Manual releases via GitHub UI
- `.github/workflows/test-pr.yml` - PR testing to TestPyPI
- `scripts/calculate_version.sh` - Shared version calculation logic

**Create a release**:
```bash
# Via GitHub UI (recommended):
# 1. Go to Actions → "Release to PyPI"
# 2. Click "Run workflow"
# 3. Select version bump type (patch/minor/major)
# 4. Click "Run workflow"
```

### 3. Programmatic Use

```python
from pypi_workflow_generator.generator import generate_workflows, initialize_project

# Initialize project
initialize_project(
    package_name="my-package",
    author="Your Name",
    author_email="your@email.com",
    description="My package",
    url="https://github.com/user/repo",
    command_name="my-cmd"
)

# Generate workflows
generate_workflows(
    python_version="3.11",
    test_path="tests/",
    verbose_publish=True
)
```

## Generated Files

This tool generates **THREE** GitHub Actions workflows and **ONE** shared script:

### 1. Release Workflow (`release.yml`)

Manual release workflow triggered via GitHub UI:

- **Version Calculation**: Automatically calculates next version (patch/minor/major)
- **Safe Tag Creation**: Creates tag locally first, tests/builds, then pushes only if successful
- **Automated Testing**: Runs pytest before publishing
- **Package Building**: Builds distribution packages
- **PyPI Publishing**: Publishes to production PyPI via Trusted Publishers
- **GitHub Release**: Creates GitHub Release with auto-generated notes
- **No PAT Required**: Uses default `GITHUB_TOKEN`
- **setuptools_scm**: Automatic versioning from git tags

### 2. PR Testing Workflow (`test-pr.yml`)

Automatically tests pull requests:

- **Triggered on PRs**: Runs automatically when PRs are opened/updated
- **Automated Testing**: Runs pytest on PR code
- **Package Building**: Builds distribution to verify it's buildable
- **TestPyPI Publishing**: Publishes pre-release to TestPyPI for testing
- **Uses Reusable Workflow**: Calls `_reusable-test-build.yml` for DRY

### 3. Reusable Test and Build Workflow (`_reusable-test-build.yml`)

Shared logic called by other workflows:

- **Parameterized**: Accepts Python version, test path, and artifact_version
- **Test Pipeline**: Checkout → setup → test → build
- **Artifact Export**: Uploads built packages for use by caller workflows
- **Version Override**: Uses `SETUPTOOLS_SCM_PRETEND_VERSION` when `artifact_version` is provided
- **Reusable**: Single source of truth for test/build logic
- **Note**: Does NOT publish (publishing done by caller workflows for PyPI Trusted Publishing compatibility)

### 4. Version Calculation Script (`scripts/calculate_version.sh`)

Shared version calculation logic used by all workflows:

- **Release Versions**: Generates semantic versions with 'v' prefix (e.g., `v1.2.3`)
- **RC Versions**: Generates pre-release versions for PRs (e.g., `1.2.3rc12345`)
- **Parameterized**: Accepts version type, bump type, PR number, and run number
- **Testable**: Can be run locally for testing version logic
- **DRY**: Eliminates ~80 lines of duplicate code across workflows

## Creating Releases

**Via GitHub Actions UI** (only method):

1. Go to **Actions** tab in your repository
2. Select **Release to PyPI** workflow
3. Click **Run workflow**
4. Choose release type:
   - **patch**: Bug fixes (0.1.0 → 0.1.1)
   - **minor**: New features (0.1.1 → 0.2.0)
   - **major**: Breaking changes (0.2.0 → 1.0.0)
5. Click **Run workflow**

The workflow will:
1. ✅ Calculate the next version number
2. ✅ Check if tag already exists remotely
3. ✅ Run tests with calculated version
4. ✅ Build package with calculated version
5. ✅ **Publish to PyPI** (critical operation first)
6. ✅ Create and push tag to repository (only after successful publish)
7. ✅ Create GitHub Release with auto-generated notes

**Key Benefit**: Tags are only created/pushed AFTER successful PyPI publish. This fail-safe design ensures:
- If publish fails, no tag is created (easy retry with same version)
- If tag push fails, package is already on PyPI (users can install), easy manual fix
- No orphaned tags for failed releases

## Version Calculation

The generator creates a shared `scripts/calculate_version.sh` script that handles version calculation for both PR and release workflows, eliminating duplicate code and ensuring consistency.

### Version Formats

- **Release versions:** `v1.2.3` (semantic versioning with 'v' prefix for git tags)
- **Development versions:** `1.2.3.dev123045` (PEP 440 dev releases for TestPyPI)
  - Format: `{version}.dev{PR_NUMBER}{RUN_NUMBER_PADDED}`
  - Example: PR #123, run #45 → `1.2.3.dev123045`
  - Run number padded to 3 digits to prevent ambiguity

### Script Usage

The script can be run locally for testing or is automatically called by workflows:

```bash
# Calculate release version (patch bump)
./scripts/calculate_version.sh --type release --bump patch
# Output: new_version=v1.2.4

# Calculate release version (minor bump)
./scripts/calculate_version.sh --type release --bump minor
# Output: new_version=v1.3.0

# Calculate development version for PR #123, run #45
./scripts/calculate_version.sh --type rc --bump patch --pr-number 123 --run-number 45
# Output: new_version=1.2.4.dev123045

# Show help
./scripts/calculate_version.sh --help
```

### How It Works

1. **Gets latest tag** from git history (defaults to v0.0.0 if none exist)
2. **Parses version** components (major, minor, patch)
3. **Applies bump** according to `--bump` parameter:
   - `major`: 1.0.0 → 2.0.0 (breaking changes)
   - `minor`: 1.2.0 → 1.3.0 (new features)
   - `patch`: 1.2.3 → 1.2.4 (bug fixes)
4. **Formats output** based on `--type`:
   - `release`: Adds 'v' prefix for git tags → `v1.2.4`
   - `rc`: No prefix, adds '.dev' + PR# + padded run# → `1.2.4.dev123045`
5. **Outputs to GitHub Actions** via `$GITHUB_OUTPUT`

### setuptools_scm Integration

The workflows use `SETUPTOOLS_SCM_PRETEND_VERSION` to ensure correct version detection:

**The Challenge:**
- Reusable workflows run in fresh GitHub Actions runners
- Tags created in one job don't exist in other jobs/runners
- setuptools_scm normally detects version from git tags
- Without tags, version detection fails

**The Solution:**
1. **Calculate version** in dedicated job using `calculate_version.sh`
2. **Pass version** to reusable workflow via `artifact_version` input parameter
3. **Build with override** using `SETUPTOOLS_SCM_PRETEND_VERSION` environment variable:
   ```yaml
   - name: Build package
     env:
       SETUPTOOLS_SCM_PRETEND_VERSION: ${{ inputs.artifact_version }}
     run: python -m build
   ```
4. **setuptools_scm respects** the override and uses provided version instead of git detection

This approach works perfectly because:
- ✅ Version calculation happens once in a job with git history
- ✅ Calculated version passes between jobs via artifacts/outputs
- ✅ Build uses explicit version, no git detection needed
- ✅ Works with PyPI Trusted Publishing (reusable workflows supported)

### Why .dev Instead of rc?

**Semantic Correctness:**
- `.dev` versions = development/pre-alpha (perfect for PR testing)
- `rc` versions = release candidates (implies near-final release ready for production)
- PR testing is exploratory development work, not release preparation

**PEP 440 Compliance:**
- `.dev` versions are the Python standard for pre-release development work
- Properly sort before official releases: `1.2.3.dev1 < 1.2.3.dev100 < 1.2.3`
- Compatible with all Python packaging tools (pip, setuptools, etc.)

**No Ambiguity:**
- Old format: `1.2.3rc12345` - impossible to determine where PR# ends and run# begins
- New format: `1.2.3.dev123045` - unambiguous (PR #123, run #45 padded to 3 digits)
- Padding to 3 digits prevents collisions between different PRs

**Examples:**
```
PR #5,    run #2   → 1.2.4.dev005002
PR #123,  run #45  → 1.2.4.dev123045
PR #1234, run #678 → 1.2.4.dev1234678
```

**Why Padding Matters:**
```
Without padding (old):
  PR #123, run #4   → 1.2.3rc1234
  PR #12,  run #34  → 1.2.3rc1234  ❌ COLLISION!
  PR #1,   run #234 → 1.2.3rc1234  ❌ COLLISION!

With padding (new):
  PR #123, run #4   → 1.2.3.dev123004  ✓
  PR #12,  run #34  → 1.2.3.dev012034  ✓
  PR #1,   run #234 → 1.2.3.dev001234  ✓
```

### Why a Shared Script?

Before using a shared script, version calculation logic was duplicated between `test-pr.yml` and `release.yml` (~80 lines of duplicate bash code). The shared script provides:

- ✅ **Single source of truth** for all version logic
- ✅ **Easier to maintain** - changes in one place affect all workflows
- ✅ **Testable** - can run locally without GitHub Actions
- ✅ **Consistent** - same logic guarantees same results
- ✅ **Extensible** - easy to add new version formats or validation rules
- ✅ **Self-documenting** - includes `--help` flag with usage examples

## Setting Up Trusted Publishers

The generated GitHub Actions workflows utilize [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/) for secure package publishing. This method enhances security by allowing your GitHub Actions workflow to authenticate with PyPI using OpenID Connect (OIDC) instead of requiring you to store sensitive API tokens as GitHub secrets.

**Why Trusted Publishers?**
- **Enhanced Security:** Eliminates the need to store PyPI API tokens, reducing the risk of token compromise.
- **Best Practice:** Recommended by PyPI for publishing from automated environments like GitHub Actions.

**How to Set Up Trusted Publishers for Your Project:**

Before your workflow can successfully publish to PyPI or TestPyPI, you must configure Trusted Publishers for your project on the respective PyPI instance.

1. **Log in to PyPI/TestPyPI:**
   - For TestPyPI: Go to `https://test.pypi.org/` and log in.
   - For official PyPI: Go to `https://pypi.org/` and log in.

2. **Navigate to Your Project's Publishing Settings:**
   - Go to your project's management page. The URL will typically look like:
     `https://[test.]pypi.org/manage/project/<your-package-name>/settings/publishing/`
   - Replace `<your-package-name>` with the actual name of your Python package (e.g., `pypi-workflow-generator`).

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

4. **Save the Publishers:** Confirm and save both publishers.

Once configured, your GitHub Actions workflows will be able to publish packages without needing any API tokens. **No PAT or GitHub App setup required!**

## That's It!

With Trusted Publishers configured, you're ready to go. The workflows use GitHub's default `GITHUB_TOKEN` for all operations - no additional authentication setup needed.

## CLI Options

### `hitoshura25-pypi-workflow-generator`

Generate all 3 GitHub Actions workflows for PyPI publishing.

```
Usage:
  hitoshura25-pypi-workflow-generator [options]

Options:
  --python-version VERSION    Python version (default: 3.11)
  --test-path PATH            Path to tests (default: .)
  --verbose-publish           Enable verbose publishing

Generates:
  .github/workflows/_reusable-test-build.yml
  .github/workflows/release.yml
  .github/workflows/test-pr.yml
```

### `hitoshura25-pypi-workflow-generator-init`

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

## MCP Server Details

The MCP server runs via stdio transport and provides three tools:

**Tool: `generate_workflows`**
- Generates all 3 GitHub Actions workflow files at once
- Creates: _reusable-test-build.yml, release.yml, and test-pr.yml
- Parameters: python_version, test_path, verbose_publish

**Tool: `initialize_project`**
- Creates pyproject.toml and setup.py
- Parameters: package_name, author, author_email, description, url, command_name

**Tool: `create_release`**
- Creates and pushes git tag
- Parameters: version

See [MCP-USAGE.md](https://github.com/hitoshura25/pypi-workflow-generator/blob/main/MCP-USAGE.md) for detailed MCP configuration and usage.

## Interface Differences

The package provides two interfaces with slightly different APIs for different use cases:

### CLI vs MCP: Release Creation

**CLI Mode** (`pypi-release`):
- Uses semantic versioning keywords: `major`, `minor`, `patch`
- Automatically increments version from latest git tag
- Convenience for developers who want simple versioning

```bash
pypi-release patch      # Creates v1.0.1 (if current is v1.0.0)
pypi-release minor      # Creates v1.1.0
pypi-release major      # Creates v2.0.0
```

**MCP Mode** (`create_release` tool):
- Accepts explicit version strings: `v1.0.0`, `v2.5.3`, etc.
- Direct control over version numbers
- Flexibility for AI agents to determine versions programmatically

```json
{
  "version": "v1.0.0"
}
```

**Why the difference?** The CLI optimizes for human convenience (automatic incrementing), while MCP optimizes for programmatic control (explicit versions).

### Entry Point Naming Convention

The MCP server uses the `mcp-` prefix (industry standard for MCP tools):
- `mcp-hitoshura25-pypi-workflow-generator` - Follows MCP ecosystem naming
- Makes it discoverable when searching for MCP servers
- Clearly distinguishes server mode from CLI mode

All other commands use the package prefix for CLI operations:
- `hitoshura25-pypi-workflow-generator`
- `hitoshura25-pypi-workflow-generator-init`
- `vmenon25-pypi-release`

## Architecture

```
User/AI Agent
      │
      ├─── MCP Mode ────────> server.py (MCP protocol)
      │                           │
      ├─── CLI Mode ────────> main.py / init.py / create_release.py
      │                           │
      └─── Programmatic ────> __init__.py
                                  │
                    All modes use shared core:
                                  ▼
                            generator.py
                      (Business logic)
```

## Dogfooding

This project uses itself to generate its own GitHub Actions workflows! The workflow files at:
- `.github/workflows/_reusable-test-build.yml`
- `.github/workflows/release.yml`
- `.github/workflows/test-pr.yml`

Were all created by running:

```bash
hitoshura25-pypi-workflow-generator \
  --python-version 3.11 \
  --test-path hitoshura25_pypi_workflow_generator/ \
  --verbose-publish
```

This ensures:
- ✅ The tool actually works (we use it ourselves)
- ✅ All 3 workflows are tested in production
- ✅ The templates stay consistent with real-world usage
- ✅ We practice what we preach
- ✅ Users can see real examples of the generated output

Check the workflow file headers to see the exact command used. Try creating a release using the GitHub Actions UI!

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
- **PyPI**: https://pypi.org/project/hitoshura25-pypi-workflow-generator/
