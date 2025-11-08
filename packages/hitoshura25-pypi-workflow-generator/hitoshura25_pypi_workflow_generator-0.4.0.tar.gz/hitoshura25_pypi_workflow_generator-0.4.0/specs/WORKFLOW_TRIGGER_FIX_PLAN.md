# Workflow Trigger Fix Implementation Plan

## Problem Statement

### The Issue
When the `create-release.yml` workflow creates and pushes a git tag using the default `GITHUB_TOKEN`, it does **not** trigger the `pypi-publish.yml` workflow, even though `pypi-publish.yml` is configured to trigger on tag pushes matching the pattern `v*.*.*`.

### Root Cause
GitHub Actions has a built-in security feature that prevents workflows triggered by `GITHUB_TOKEN` from triggering other workflows. This is intentional behavior designed to:
- Prevent infinite workflow loops
- Avoid security issues with recursive triggers
- Limit resource consumption from cascading workflows

**GitHub Documentation Reference:**
> "When you use the repository's GITHUB_TOKEN to perform tasks, events triggered by the GITHUB_TOKEN will not create a new workflow run."

### Impact
- Users who create releases via the GitHub Actions UI (using `create-release.yml`) find that their package is **not** automatically published to PyPI
- This breaks the promised "zero-touch" automation experience
- Users must manually trigger the `pypi-publish.yml` workflow or use the CLI `pypi-release` command instead

## Solution Design

### Approach: Configurable Personal Access Token (PAT)

Use a Personal Access Token (PAT) instead of `GITHUB_TOKEN` when pushing tags. This allows the tag push to trigger other workflows.

### Key Design Decisions

1. **Configurable with Sensible Default**
   - Default secret name: `RELEASE_PAT`
   - Users can override with custom secret name via workflow input
   - 95% of users: Just create `RELEASE_PAT` and it works
   - 5% of users (enterprise, multi-repo): Can specify custom token names

2. **Workflow Input Parameter**
   ```yaml
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
       token_secret_name:  # NEW
         description: 'Name of the GitHub PAT secret to use (default: RELEASE_PAT)'
         required: false
         type: string
         default: 'RELEASE_PAT'
   ```

3. **Dynamic Secret Reference**
   GitHub Actions allows dynamic secret lookup using:
   ```yaml
   secrets[inputs.token_secret_name]
   ```
   This enables runtime selection of which secret to use.

4. **Graceful Fallback**
   If the specified secret doesn't exist, the workflow should fail with a clear error message explaining:
   - Which secret it tried to use
   - How to create the required PAT
   - Where to add it to repository secrets

### Why This Design?

**Pros:**
- ✅ Simple for most users: "Create RELEASE_PAT, done"
- ✅ Flexible for advanced users: Can specify org-wide tokens
- ✅ Clear documentation path: Single standard name to document
- ✅ Future-proof: Can support GitHub Apps tokens, deploy keys, etc.
- ✅ No breaking changes: Existing workflows won't break (they'll just need setup)

**Cons:**
- ⚠️ Requires manual setup (creating PAT + adding secret)
- ⚠️ Security consideration: PATs have broader permissions than GITHUB_TOKEN
- ⚠️ Token management: Users need to handle token rotation

## Implementation Details

### 1. Template Changes: `create_release.yml.j2`

**Location:** `pypi_workflow_generator/create_release.yml.j2`

#### A. Add workflow input parameter

```yaml
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
      token_secret_name:
        description: 'Name of the GitHub PAT secret to use for triggering workflows (default: RELEASE_PAT)'
        required: false
        type: string
        default: 'RELEASE_PAT'
```

#### B. Update job to use the PAT

Add a new step after checkout to validate the token exists:

```yaml
- name: Validate PAT secret
  id: validate_token
  run: |
    if [ -z "${{ secrets[github.event.inputs.token_secret_name || 'RELEASE_PAT'] }}" ]; then
      echo "::error::Secret '${{ github.event.inputs.token_secret_name || 'RELEASE_PAT' }}' not found"
      echo "::error::Please create a Personal Access Token with 'repo' scope and add it as a repository secret"
      echo "::error::See: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token"
      exit 1
    fi
    echo "Token validated successfully"
```

#### C. Update tag push step to use PAT

Replace the existing "Create and push tag" step:

**Before:**
```yaml
- name: Create and push tag
  run: |
    new_version="${{ steps.calc_version.outputs.new_version }}"
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git tag -a "$new_version" -m "Release $new_version"
    git push origin "$new_version"
    echo "✅ Created and pushed tag: $new_version"
```

**After:**
```yaml
- name: Create and push tag
  env:
    GITHUB_TOKEN: ${{ secrets[github.event.inputs.token_secret_name || 'RELEASE_PAT'] }}
  run: |
    new_version="${{ steps.calc_version.outputs.new_version }}"

    # Configure git to use the PAT for authentication
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"

    # Create annotated tag
    git tag -a "$new_version" -m "Release $new_version"

    # Push tag using PAT (this will trigger other workflows)
    git push https://x-access-token:${GITHUB_TOKEN}@github.com/${{ github.repository }}.git "$new_version"

    echo "✅ Created and pushed tag: $new_version"
```

#### D. Update summary to mention workflow triggering

```yaml
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
    echo "[View Publish Workflow](https://github.com/${{ github.repository }}/actions/workflows/pypi-publish.yml)" >> $GITHUB_STEP_SUMMARY
```

### 2. Regenerate Dogfooding Workflow

**Location:** `.github/workflows/create-release.yml`

After updating the template, regenerate this project's own workflow:

```bash
python -m pypi_workflow_generator.release_workflow
```

This ensures we're dogfooding the new implementation.

### 3. Documentation Updates

#### A. README.md Updates

**New Section: "Setting Up Automated Release Publishing"**

Add after the "Setting Up Trusted Publishers" section:

```markdown
## Setting Up Automated Release Publishing

### Why You Need a Personal Access Token

GitHub Actions workflows triggered by the default `GITHUB_TOKEN` cannot trigger other workflows (security feature). To enable the `create-release.yml` workflow to automatically trigger `pypi-publish.yml`, you need to provide a Personal Access Token (PAT) with appropriate permissions.

### Creating the Required PAT

1. **Generate a Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Give it a descriptive name: `Release Automation Token for <repo-name>`
   - Set expiration (recommended: 1 year, with calendar reminder)
   - Select scope: **repo** (full control of private repositories)
   - Click "Generate token"
   - **Copy the token immediately** (you won't see it again)

2. **Add Token to Repository Secrets**:
   - Go to your repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `RELEASE_PAT`
   - Value: Paste the token you copied
   - Click "Add secret"

3. **Verify Setup**:
   - Go to Actions tab → Create Release workflow → Run workflow
   - Select release type (patch/minor/major)
   - The workflow should complete successfully
   - The PyPI publish workflow should trigger automatically
   - Your package should be published to PyPI

### Using a Custom Token Name (Optional)

If your organization uses a different secret name (e.g., `GITHUB_ORG_TOKEN`), you can specify it when running the workflow:

1. Go to Actions → Create Release
2. Click "Run workflow"
3. Fill in:
   - Release type: patch/minor/major
   - Token secret name: `GITHUB_ORG_TOKEN` (or your custom name)

### Security Considerations

- **Token Scope**: The PAT needs `repo` scope to push tags and trigger workflows
- **Token Rotation**: Set expiration dates and rotate tokens regularly
- **Access Control**: Only repository admins can add/view secrets
- **Audit**: GitHub logs all token usage in the audit log

### Troubleshooting

**Workflow fails with "Secret 'RELEASE_PAT' not found"**
- You haven't created the PAT or added it to repository secrets
- Follow the steps above to create and add the token

**PyPI publish workflow still doesn't trigger**
- Verify the PAT has `repo` scope (not just `public_repo`)
- Check that the token hasn't expired
- Ensure the token is added to repository secrets (not environment secrets)

**Alternative: Use CLI Method**
If you prefer not to set up a PAT, you can create releases locally:
```bash
pypi-release patch  # This runs on your machine, no PAT needed
```
```

#### B. Update "Creating Releases" Section

Update the GitHub Actions UI section to mention the PAT requirement:

```markdown
### Option 1: GitHub Actions UI (Recommended)

**Prerequisites**: Create a `RELEASE_PAT` secret (see "Setting Up Automated Release Publishing" above)

1. Go to **Actions** tab in your repository
2. Select **Create Release** workflow
3. Click **Run workflow**
4. Choose release type:
   - **patch**: Bug fixes (0.1.0 → 0.1.1)
   - **minor**: New features (0.1.1 → 0.2.0)
   - **major**: Breaking changes (0.2.0 → 1.0.0)
5. (Optional) Specify custom token secret name if not using `RELEASE_PAT`
6. Click **Run workflow**

The workflow will:
- Calculate the next version number
- Create and push a git tag
- Create a GitHub Release with auto-generated notes
- **Automatically trigger the PyPI publish workflow** (requires RELEASE_PAT)
- Publish your package to PyPI
```

#### C. MCP-USAGE.md Updates

**Add to FAQ section:**

```markdown
**Q: Why does the release workflow need a Personal Access Token?**
A: GitHub Actions workflows triggered by the default `GITHUB_TOKEN` cannot trigger other workflows (security feature). To automatically trigger the PyPI publish workflow after creating a release, you need to provide a PAT with `repo` scope as a repository secret named `RELEASE_PAT`. See the README for detailed setup instructions.

**Q: Can I use the MCP tool to create releases without a PAT?**
A: Yes! The MCP `create_release` tool runs locally on your machine (not in GitHub Actions), so it doesn't have this limitation. It will trigger the PyPI publish workflow without needing a PAT.
```

**Update "Available Tools" section for generate_release_workflow:**

```markdown
### 4. generate_release_workflow

Generate GitHub Actions workflow for creating releases via UI. This allows manual release creation with automatic version calculation and tag creation.

**Parameters**:
- `output_filename` (string, optional): Workflow filename, default "create-release.yml"

**Example**:
```json
{
  "output_filename": "create-release.yml"
}
```

**Returns**:
- Success message with file path
- Error message if workflow generation fails

**Use Case**: Use this when you only want to add the release creation workflow to an existing project, or when you used `include_release_workflow: false` with `generate_workflow`.

**Important Setup Note**: The generated workflow requires a Personal Access Token (PAT) to trigger the PyPI publish workflow. Users must:
1. Create a PAT with `repo` scope
2. Add it as a repository secret named `RELEASE_PAT`
3. See the README for detailed instructions

**Workflow Features**:
- Manual trigger via GitHub Actions UI
- Choose major/minor/patch version bump
- Automatic version calculation from latest git tag
- Creates and pushes git tag using PAT
- Creates GitHub Release with auto-generated notes
- Automatically triggers PyPI publish workflow
```

### 4. Add Token Secret Name to Generator Function (Optional)

**Decision Point**: Should we add `token_secret_name` as a parameter to `generate_release_workflow()`?

**Recommendation**: No, keep it simple. The token name should be configured at workflow runtime, not at generation time. Reasons:
- Different repos may use different secret names
- Token names can change over time without regenerating workflows
- The workflow input provides sufficient flexibility
- Keeps the generator API clean and simple

If we wanted to add it anyway (for advanced use cases):

```python
def generate_release_workflow(
    output_filename: str = 'create-release.yml',
    base_output_dir: Optional[str] = None,
    default_token_secret_name: str = 'RELEASE_PAT'  # NEW (optional)
) -> Dict[str, Any]:
    """
    Generate GitHub Actions workflow for automated release creation.

    Args:
        output_filename: Name of generated workflow file
        base_output_dir: Custom output directory
        default_token_secret_name: Default PAT secret name (default: 'RELEASE_PAT')
    """
    # ... existing code ...

    # Render template with token name
    workflow_content = template.render(
        default_token_secret_name=default_token_secret_name
    )
```

**Decision**: Skip this for now. Add only if users request it.

## Testing Strategy

**Primary Testing Method: Dogfooding (Using This Tool on Itself)**

This project practices **"dogfooding"** - using pypi-workflow-generator to generate its own GitHub Actions workflows. This is the BEST way to validate that the tool works correctly because:

- ✅ **Real-world validation**: We generate workflows for an actual Python package (this one!)
- ✅ **End-to-end testing**: We can run the generated workflows in production
- ✅ **Quality assurance**: Any issues will affect us directly, ensuring we ship quality code
- ✅ **Living documentation**: The workflows in `.github/workflows/` serve as examples for users
- ✅ **Confidence**: If it works for us, it will work for our users

**What is Dogfooding?**

"Dogfooding" comes from "eating your own dog food" - if we're confident enough to use our own tool to manage our releases, users can be confident too. In practice, this means:

1. We run `pypi-workflow-generator` commands to generate this repo's workflows
2. We use the generated `create-release.yml` to create our releases
3. We verify that `pypi-publish.yml` triggers automatically
4. We confirm the package publishes to PyPI successfully

### 1. Primary Test: Dogfooding (THIS REPOSITORY)

**Objective**: Regenerate this project's workflows using the updated template and verify they work in production.

**Why This is the Primary Test:**
- Validates the template generates valid YAML
- Confirms the PAT configuration works correctly
- Tests the actual GitHub Actions execution environment
- Proves the workflow chain (create-release → pypi-publish) works
- Validates all documentation matches real behavior

**Detailed Process:**

#### Step 1: Update the Template
```bash
# Edit pypi_workflow_generator/create_release.yml.j2 with PAT changes
```

#### Step 2: Regenerate This Repo's Workflow
```bash
# Use the tool to generate workflows for itself (dogfooding!)
python -m pypi_workflow_generator.release_workflow

# Expected output:
# Successfully generated .github/workflows/create-release.yml
```

#### Step 3: Verify Generated Workflow
```bash
# Check that the generated workflow has:
# - token_secret_name input parameter
# - PAT validation step
# - Git authentication using the PAT
# - Clear error messages

cat .github/workflows/create-release.yml
```

**Verification Checklist:**
- [ ] Workflow has `token_secret_name` input with default `RELEASE_PAT`
- [ ] Workflow validates the secret exists before using it
- [ ] Git push uses PAT: `https://x-access-token:${GITHUB_TOKEN}@github.com/...`
- [ ] Error messages mention how to create PAT
- [ ] Summary links to publish workflow

#### Step 4: Set Up PAT for This Repository
```bash
# 1. Create a GitHub PAT:
#    - Go to github.com → Settings → Developer settings → Personal access tokens
#    - Generate new token (classic)
#    - Name: "pypi-workflow-generator release automation"
#    - Scope: repo (full control)
#    - Expiration: 1 year (set calendar reminder)
#    - Copy the token

# 2. Add to repository secrets:
#    - Go to this repo → Settings → Secrets and variables → Actions
#    - New repository secret
#    - Name: RELEASE_PAT
#    - Value: <paste token>
#    - Save
```

#### Step 5: Test Release Creation
```bash
# Option A: Via GitHub UI (tests the full user experience)
# 1. Go to Actions tab
# 2. Select "Create Release" workflow
# 3. Click "Run workflow"
# 4. Select "patch" (will create v0.3.0 or next version)
# 5. Leave token_secret_name as default
# 6. Click "Run workflow"

# Option B: Verify workflow file locally first
# (Check YAML syntax, validate structure)
yamllint .github/workflows/create-release.yml
```

#### Step 6: Verify Complete Flow
After triggering the workflow, verify:

**Create Release Workflow:**
- [ ] Workflow starts successfully
- [ ] Latest tag is detected correctly
- [ ] New version is calculated correctly
- [ ] Tag is created and pushed
- [ ] GitHub Release is created with auto-generated notes
- [ ] Workflow completes successfully
- [ ] Summary shows link to publish workflow

**PyPI Publish Workflow (Should trigger automatically):**
- [ ] Workflow is triggered by the tag push
- [ ] Tests run and pass
- [ ] Package builds successfully
- [ ] Package publishes to TestPyPI (if on a PR)
- [ ] Package publishes to PyPI (if on a tag)
- [ ] New version appears on PyPI

**Final Verification:**
```bash
# Verify the new version is on PyPI
pip install pypi-workflow-generator==0.3.0  # (or whatever version was created)

# Verify it installs and works
pypi-workflow-generator --help
```

#### Step 7: Document Results
- Take screenshots of successful workflow runs
- Note any issues encountered
- Document the exact steps that worked
- Update troubleshooting section if needed

**Expected Outcome:**
- ✅ Workflow generates successfully
- ✅ Release creation workflow runs successfully
- ✅ Tag is pushed
- ✅ PyPI publish workflow triggers automatically (NOT manually!)
- ✅ Package publishes to PyPI
- ✅ New version is available for installation

**If Dogfooding Fails:**
- 🚫 **DO NOT** merge the PR
- 🚫 **DO NOT** release the changes
- ✅ Fix the issues
- ✅ Regenerate workflows
- ✅ Test again until dogfooding succeeds

### 2. Unit Tests

No new unit tests required for this change because:
- The template generation logic remains the same
- The dynamic secret reference is a GitHub Actions feature, not our code
- We can't easily test GitHub Actions secret resolution in unit tests

**Note:** Dogfooding serves as our integration test.

### 3. Additional Manual Tests (Optional)

These tests can be performed on a separate test repository if desired, but **dogfooding is sufficient** for validating the implementation.

**Test Plan:**

#### Test 1: Custom Token Name
1. In this repository, add a secret named `CUSTOM_RELEASE_TOKEN` (in addition to RELEASE_PAT)
2. Trigger create-release workflow via UI
3. Enter "CUSTOM_RELEASE_TOKEN" in the token_secret_name input field
4. Verify workflow completes and triggers pypi-publish

#### Test 2: Missing Token (Error Handling)
1. Temporarily rename RELEASE_PAT secret to something else
2. Trigger create-release workflow
3. Verify:
   - Workflow fails immediately with clear error message
   - Error explains which secret is missing (RELEASE_PAT)
   - Error includes instructions for creating the PAT
4. Restore RELEASE_PAT secret

#### Test 3: Invalid Token (Error Handling)
1. Temporarily replace RELEASE_PAT value with an invalid token (e.g., "invalid-token-123")
2. Trigger workflow
3. Verify:
   - Workflow progresses through tag creation
   - Git push fails with authentication error
   - Error message is clear about authentication failure
4. Restore valid RELEASE_PAT value

#### Test 4: Token Without Repo Scope
1. Create a PAT with only `public_repo` scope (not full `repo`)
2. Add as RELEASE_PAT_TEST
3. Trigger workflow with custom token name
4. Expected result:
   - May succeed for public repos
   - Will fail for private repos with permission error
5. Document the importance of full `repo` scope

## Files to Modify

### Must Change
1. ✅ `pypi_workflow_generator/create_release.yml.j2` - Update template
2. ✅ `.github/workflows/create-release.yml` - Regenerate for dogfooding
3. ✅ `README.md` - Add PAT setup section, update creating releases section
4. ✅ `MCP-USAGE.md` - Add FAQ entry, update tool documentation

### Should Consider
5. ⚠️ `pypi_workflow_generator/generator.py` - Add token_secret_name parameter? (Decision: Skip for now)
6. ⚠️ `pypi_workflow_generator/server.py` - Add to MCP tool schema? (Decision: Skip for now)

### No Changes Needed
7. ❌ `pypi_workflow_generator/tests/test_release_workflow.py` - No unit tests needed
8. ❌ `setup.py` - No changes needed
9. ❌ `pypi_publish.yml.j2` - No changes needed (already configured correctly)

## Rollout Considerations

### Breaking vs Non-Breaking Change

**This is a BREAKING change** for users who:
- Already deployed the create-release.yml workflow
- Expect it to trigger pypi-publish automatically
- Haven't set up a PAT

**Mitigation:**
1. Clear documentation in README and release notes
2. Graceful error messages when PAT is missing
3. Provide alternative (CLI method) that doesn't require PAT
4. Document in release notes as "BREAKING: Requires PAT setup"

### Migration Guide for Existing Users

**In Release Notes:**

```markdown
## 🚨 Breaking Change: Release Workflow Requires PAT

### What Changed
The `create-release.yml` workflow now requires a Personal Access Token (PAT) to automatically trigger the PyPI publish workflow.

### Why This Change
GitHub Actions workflows using the default `GITHUB_TOKEN` cannot trigger other workflows (security feature). This prevented automatic PyPI publishing after creating releases.

### Action Required
To continue using the GitHub Actions UI release method:

1. Create a GitHub PAT with `repo` scope
2. Add it to your repository secrets as `RELEASE_PAT`
3. See [Setting Up Automated Release Publishing](#setting-up-automated-release-publishing) for detailed instructions

### Alternatives
- **Use CLI method**: `pypi-release patch` (runs locally, no PAT needed)
- **Manual trigger**: Create release via workflow, then manually trigger pypi-publish workflow

### Timeline
- This change affects all new workflow generations
- Existing workflows will continue to work but won't trigger pypi-publish
- Add the PAT at your convenience
```

### Version Bump

This should be a **minor version bump** (e.g., 0.2.1 → 0.3.0) because:
- It adds new functionality (configurable token)
- It requires user action (breaking for some use cases)
- It changes generated workflow behavior

## Security Considerations

### PAT Permissions

**Minimum Required Scope:**
- `repo` - Full control of private repositories

**Why `repo` and not `public_repo`?**
- `public_repo` only works for public repositories
- `repo` works for both public and private repositories
- Users with private repos need the broader scope
- Better to standardize on one scope for simplicity

### Token Storage

- ✅ Stored as GitHub repository secret (encrypted at rest)
- ✅ Only accessible to workflow runners
- ✅ Not exposed in logs
- ✅ Only repository admins can view/modify

### Token Rotation

- ⚠️ Users must manually rotate tokens
- ⚠️ Recommend setting expiration dates (1 year)
- ⚠️ Document rotation process in README

### Alternative: GitHub Apps

**Future Enhancement**: Support GitHub Apps tokens as an alternative to PATs.

**Pros:**
- More fine-grained permissions
- Better audit trail
- Automatic rotation
- Organization-wide installation

**Cons:**
- More complex setup
- Requires creating a GitHub App
- May be overkill for simple use cases

**Decision**: Start with PAT, document GitHub Apps as future enhancement.

## Open Questions

### Q1: Should we support fallback to GITHUB_TOKEN?
**Answer**: No. If we fall back, users won't realize the workflow isn't triggering pypi-publish. Better to fail loudly with a clear error message.

### Q2: Should we make token_secret_name configurable at generation time?
**Answer**: No. Keep it simple. Configure at runtime via workflow input. This allows different repos to use different secrets without regenerating workflows.

### Q3: Should we support multiple token types (PAT, GitHub Apps, deploy keys)?
**Answer**: Start with PAT. GitHub Apps can be future enhancement if users request it.

### Q4: Should we validate token permissions in the workflow?
**Answer**: Difficult to validate at workflow runtime. Rely on clear error messages when git push fails. Document required scopes clearly.

### Q5: How do we handle token expiration?
**Answer**: Document best practices (set expiration, calendar reminder). Workflow will fail with auth error when token expires, which is acceptable.

## Success Criteria

### Primary Success Criteria (Dogfooding)
1. ✅ **Dogfooding: Successfully regenerated `.github/workflows/create-release.yml` for this repository**
2. ✅ **Dogfooding: Successfully created a release using the generated workflow**
3. ✅ **Dogfooding: PyPI publish workflow triggered automatically (not manually)**
4. ✅ **Dogfooding: Package published to PyPI successfully**

### Implementation Success Criteria
5. ✅ Template generates valid YAML with PAT configuration
6. ✅ Users can create releases via GitHub Actions UI with PAT
7. ✅ Tags pushed with PAT automatically trigger pypi-publish workflow
8. ✅ Clear documentation for PAT setup in README.md
9. ✅ Graceful error messages when token is missing
10. ✅ Works with both default (`RELEASE_PAT`) and custom token names
11. ✅ No breaking changes for CLI method (`pypi-release` command)

### Quality Criteria
12. ✅ All 23 existing tests continue to pass
13. ✅ Generated workflow passes GitHub Actions YAML validation
14. ✅ Error messages include actionable next steps for users

## Timeline

**Estimated Implementation Time**: 2-3 hours
- Template changes: 30 minutes
- Documentation updates: 60 minutes
- **Dogfooding (primary testing)**: 60 minutes
- Review and refinement: 30 minutes

**Dogfooding Testing Time Breakdown**: 60 minutes
- Regenerate this repo's workflow: 5 minutes
- Create and configure PAT: 10 minutes
- Trigger workflow and verify: 15 minutes
- Verify PyPI publish triggers: 15 minutes
- Verify package on PyPI: 10 minutes
- Document results: 5 minutes

**Total**: 2.5-3.5 hours

## Next Steps

### Phase 1: Implementation
1. ✅ Get approval on this implementation plan
2. 🔄 Implement template changes (`create_release.yml.j2`)
3. 🔄 Update documentation (README.md, MCP-USAGE.md)

### Phase 2: Dogfooding (Critical - DO NOT SKIP)
4. 🔄 **Regenerate this repo's workflows using the updated template**
5. 🔄 **Create PAT for this repository**
6. 🔄 **Test release creation on this repository**
7. 🔄 **Verify PyPI publish triggers automatically**
8. 🔄 **Verify package publishes successfully**

### Phase 3: Release
9. 🔄 Document in release notes as breaking change
10. 🔄 Create release (using the dogfooded workflow!)

**Critical Rule:**
- ⚠️ **DO NOT proceed to Phase 3 until Phase 2 dogfooding succeeds**
- ⚠️ **DO NOT merge PR until dogfooding validates the implementation**

## References

- [GitHub Actions: Triggering a workflow from a workflow](https://docs.github.com/en/actions/using-workflows/triggering-a-workflow#triggering-a-workflow-from-a-workflow)
- [GitHub Actions: Automatic token authentication](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)
- [Creating a personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Using secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)
