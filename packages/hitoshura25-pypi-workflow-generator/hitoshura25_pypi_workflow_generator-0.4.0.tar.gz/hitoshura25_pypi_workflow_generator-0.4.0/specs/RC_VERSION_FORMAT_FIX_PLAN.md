# PLAN: Fix RC Version Format for TestPyPI Pre-releases

**Date:** 2025-11-05
**Issue:** Current RC version format has ambiguity and unnecessarily large version numbers
**Current Format:** `1.2.3rc12345` (PR #123 + run #45 = rc12345)
**Recommended:** Use development versions with proper formatting per PEP 440

---

## Problem Statement

### Current Implementation Issues

**The current format concatenates PR number with run number:**
```bash
# PR #123, run #45
new_version="${major}.${minor}.${patch}rc${PR_NUMBER}${RUN_NUMBER}"
# Results in: 1.2.3rc12345
```

**Problems:**

1. **Ambiguity Risk:**
   - PR #123, run #4 → `1.2.3rc1234`
   - PR #12, run #34 → `1.2.3rc1234` ❌ **COLLISION!**
   - Different PRs can generate identical version numbers

2. **Large Version Numbers:**
   - PR #1234, run #5 → `1.2.3rc12345`
   - PR #500, run #100 → `1.2.3rc500100`
   - Unnecessarily large numeric suffixes

3. **No PR Traceability:**
   - Given `1.2.3rc12345`, hard to determine:
     - Was it PR #123 run #45?
     - Was it PR #1234 run #5?
     - Was it PR #1 run #2345?

4. **Semantic Incorrectness:**
   - `rc` (release candidate) implies near-final release
   - PR testing is actually development/pre-alpha work
   - Should use `.dev` versions instead

---

## Python Version Format Standards (PEP 440)

### Valid Pre-release Version Formats

Python's PEP 440 defines these pre-release version types:

```
Development releases:  1.2.3.dev456
Alpha releases:        1.2.3a1
Beta releases:         1.2.3b2
Release candidates:    1.2.3rc3
Post-releases:         1.2.3.post1
```

### What's Appropriate for PR Testing?

| Version Type | Use Case | Example | Appropriate? |
|--------------|----------|---------|--------------|
| `.dev` | Development/pre-alpha versions | `1.2.3.dev123` | ✅ **Best choice** |
| `a` (alpha) | Alpha releases | `1.2.3a1` | ⚠️ Too formal for PRs |
| `b` (beta) | Beta releases | `1.2.3b1` | ⚠️ Too formal for PRs |
| `rc` | Release candidates | `1.2.3rc1` | ❌ Wrong semantics |
| `.post` | Post-releases | `1.2.3.post1` | ❌ Wrong direction |

**Verdict:** Use `.dev` versions for PR testing on TestPyPI.

### PEP 440 Ordering

Development versions sort correctly:
```
1.2.3.dev1 < 1.2.3.dev2 < 1.2.3.dev100 < 1.2.3 < 1.2.3.post1
```

This means:
- All `.dev` versions come before the final release
- Numeric ordering works correctly
- TestPyPI versions won't interfere with PyPI versions

---

## Solution Analysis

### Option 1: GitHub Run Number Only

**Format:** `1.2.4.dev${GITHUB_RUN_NUMBER}`

**Example:**
```bash
# Any PR, run #1234
new_version="1.2.4.dev1234"
```

**Pros:**
- ✅ Guaranteed unique (GitHub run numbers are globally unique per repo)
- ✅ Short and clean
- ✅ Simple to implement
- ✅ Sortable

**Cons:**
- ❌ No indication which PR it came from
- ❌ Hard to trace back to PR without checking GitHub Actions

**Use Case:** Best if you don't need to identify PR from version number.

---

### Option 2: Timestamp-Based

**Format:** `1.2.4.dev${EPOCH_SECONDS}`

**Example:**
```bash
# November 5, 2025, 8:30 PM UTC
new_version="1.2.4.dev1730838600"
```

**Pros:**
- ✅ Guaranteed unique
- ✅ Chronologically sortable
- ✅ Universal standard

**Cons:**
- ❌ Very large numbers (10 digits)
- ❌ No PR or run information
- ❌ Harder to read/remember

**Use Case:** Best if chronological ordering is critical.

---

### Option 3: PR Number + Padded Run Number ⭐ **RECOMMENDED**

**Format:** `1.2.4.dev${PR_NUMBER}${RUN_NUMBER_PADDED_TO_3_DIGITS}`

**Example:**
```bash
# PR #123, run #45
new_version="1.2.4.dev123045"

# PR #5, run #2
new_version="1.2.4.dev005002"

# PR #1234, run #678
new_version="1.2.4.dev1234678"
```

**Padding Logic:**
```bash
# Pad run number to 3 digits (supports 0-999 runs per PR)
printf -v padded_run "%03d" "$RUN_NUMBER"
new_version="${major}.${minor}.${patch}.dev${PR_NUMBER}${padded_run}"
```

**Pros:**
- ✅ **No ambiguity** (padding prevents collisions)
- ✅ **PR traceability** (can identify source PR)
- ✅ **Reasonable size** (typically 6-7 digits)
- ✅ **PEP 440 compliant**
- ✅ **Sortable** (within same PR, chronological)

**Cons:**
- ⚠️ Slightly longer than option 1
- ⚠️ Assumes <1000 runs per PR (reasonable assumption)

**Why This Works:**
- PR #123, run #4  → `1.2.4.dev123004`
- PR #12, run #34  → `1.2.4.dev012034`
- **No collision!**

**Use Case:** ⭐ Best for most projects - balances traceability and clarity.

---

### Option 4: Local Version Identifiers

**Format:** `1.2.4.dev0+pr123.run45`

**Example:**
```bash
# PR #123, run #45
new_version="1.2.4.dev0+pr123.run45"
```

**Pros:**
- ✅ Clean dev number
- ✅ Full PR/run metadata
- ✅ PEP 440 compliant
- ✅ Very readable

**Cons:**
- ❌ More complex to parse
- ❌ May not sort correctly on TestPyPI
- ❌ Some tools don't handle local versions well

**Use Case:** Best if human readability is paramount, and tools support local versions.

---

## Recommended Solution: Option 3

### Implementation Details

**Version Format:** `{major}.{minor}.{patch}.dev{PR_NUMBER}{RUN_NUMBER_PADDED}`

**Key Features:**
1. Use `.dev` instead of `rc` (semantically correct)
2. Pad run number to 3 digits (prevents ambiguity)
3. Keep PR number for traceability
4. Total length: ~10 characters (e.g., `1.2.3.dev123045`)

**Padding Examples:**
```
PR #5,    run #2   → 1.2.4.dev005002
PR #123,  run #45  → 1.2.4.dev123045
PR #1000, run #500 → 1.2.4.dev1000500
```

**Advantages over current approach:**
- ❌ Old: `1.2.3rc12345` (ambiguous: PR #123 run #45 OR PR #1234 run #5?)
- ✅ New: `1.2.3.dev123045` (unambiguous: PR #123, run #45)

---

## Implementation Plan

### Update `scripts/calculate_version.sh.j2`

**Line ~258-263 (RC version generation):**

**Current Code:**
```bash
elif [[ "$VERSION_TYPE" == "rc" ]]; then
  # RC version format: major.minor.patch + "rc" + PR# + RUN#
  # Example: 1.2.3rc12345 (PR 123, run 45)
  new_version="${major}.${minor}.${patch}rc${PR_NUMBER}${RUN_NUMBER}"
  echo -e "${GREEN}Generated RC version: $new_version${NC}" >&2
fi
```

**New Code:**
```bash
elif [[ "$VERSION_TYPE" == "rc" ]]; then
  # Development version format: major.minor.patch.dev + PR# + padded RUN#
  # Pad run number to 3 digits to prevent ambiguity
  # Example: 1.2.3.dev123045 (PR 123, run 45)
  printf -v padded_run "%03d" "$RUN_NUMBER"
  new_version="${major}.${minor}.${patch}.dev${PR_NUMBER}${padded_run}"
  echo -e "${GREEN}Generated dev version: $new_version${NC}" >&2
fi
```

### Update Help Documentation in Script

**Line ~54-67 (help examples):**

**Current:**
```bash
EXAMPLES:
  # Release version (patch bump)
  calculate_version.sh --type release --bump patch
  # Output: new_version=v1.2.4

  # RC version for PR #123, run #45
  calculate_version.sh --type rc --bump patch --pr-number 123 --run-number 45
  # Output: new_version=1.2.4rc12345
```

**New:**
```bash
EXAMPLES:
  # Release version (patch bump)
  calculate_version.sh --type release --bump patch
  # Output: new_version=v1.2.4

  # Development version for PR #123, run #45
  calculate_version.sh --type rc --bump patch --pr-number 123 --run-number 45
  # Output: new_version=1.2.4.dev123045
```

### Update README.md

**Section: "Version Formats" (line ~205-208):**

**Current:**
```markdown
### Version Formats

- **Release versions:** `v1.2.3` (semantic versioning with 'v' prefix for git tags)
- **RC versions:** `1.2.3rc12345` (no 'v' prefix, includes PR number and run number for TestPyPI)
```

**New:**
```markdown
### Version Formats

- **Release versions:** `v1.2.3` (semantic versioning with 'v' prefix for git tags)
- **Development versions:** `1.2.3.dev123045` (PEP 440 dev releases for TestPyPI)
  - Format: `{version}.dev{PR_NUMBER}{RUN_NUMBER_PADDED}`
  - Example: PR #123, run #45 → `1.2.3.dev123045`
  - Run number padded to 3 digits to prevent ambiguity
```

**Section: "Script Usage" (line ~214-225):**

**Current:**
```bash
# Calculate RC version for PR #123, run #45
./scripts/calculate_version.sh --type rc --bump patch --pr-number 123 --run-number 45
# Output: new_version=1.2.4rc12345
```

**New:**
```bash
# Calculate development version for PR #123, run #45
./scripts/calculate_version.sh --type rc --bump patch --pr-number 123 --run-number 45
# Output: new_version=1.2.4.dev123045
```

**Section: "How It Works" (line ~239-241):**

**Current:**
```markdown
4. **Formats output** based on `--type`:
   - `release`: Adds 'v' prefix for git tags → `v1.2.4`
   - `rc`: No prefix, adds 'rc' + PR# + run# → `1.2.4rc12345`
```

**New:**
```markdown
4. **Formats output** based on `--type`:
   - `release`: Adds 'v' prefix for git tags → `v1.2.4`
   - `rc`: No prefix, adds '.dev' + PR# + padded run# → `1.2.4.dev123045`
```

### Add New Section to README: "Why Development Versions?"

**Insert after "Version Formats":**

```markdown
### Why .dev Instead of rc?

**Semantic Correctness:**
- `.dev` versions = development/pre-alpha (perfect for PR testing)
- `rc` versions = release candidates (implies near-final release)
- PR testing is exploratory, not release preparation

**PEP 440 Compliance:**
- `.dev` versions are the standard for pre-release development work
- Properly sort before official releases: `1.2.3.dev1 < 1.2.3`
- Compatible with all Python packaging tools

**No Ambiguity:**
- Old format: `1.2.3rc12345` - impossible to determine PR vs run split
- New format: `1.2.3.dev123045` - PR #123, run #45 (padded to 3 digits)
- Padding prevents collisions between different PRs

**Examples:**
```
PR #5,    run #2   → 1.2.4.dev005002
PR #123,  run #45  → 1.2.4.dev123045
PR #1234, run #678 → 1.2.4.dev1234678
```
```

---

## Testing Plan

### 1. Update Script Template

Update `pypi_workflow_generator/scripts/calculate_version.sh.j2` with new logic.

### 2. Add Test Cases

Add to `pypi_workflow_generator/tests/test_calculate_version.py`:

```python
def test_dev_version_format_padding(tmp_path):
    """Test that dev versions properly pad run numbers."""
    from pypi_workflow_generator.generator import generate_workflows

    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Create required files
        (tmp_path / 'pyproject.toml').write_text('[build-system]')
        (tmp_path / 'setup.py').write_text('# setup')

        generate_workflows(
            python_version='3.11',
            test_path='tests/'
        )

        script_path = tmp_path / 'scripts' / 'calculate_version.sh'
        content = script_path.read_text()

        # Should use .dev instead of rc
        assert '.dev' in content, "Script should generate .dev versions"
        assert 'printf -v padded_run "%03d"' in content, "Script should pad run numbers"

    finally:
        os.chdir(original_cwd)
```

### 3. Manual Testing

Test the script with various inputs:

```bash
# Small PR, small run
./scripts/calculate_version.sh --type rc --bump patch --pr-number 5 --run-number 2
# Expected: 1.2.4.dev005002

# Medium PR, medium run
./scripts/calculate_version.sh --type rc --bump patch --pr-number 123 --run-number 45
# Expected: 1.2.4.dev123045

# Large PR, large run
./scripts/calculate_version.sh --type rc --bump patch --pr-number 1234 --run-number 678
# Expected: 1.2.4.dev1234678
```

### 4. Integration Testing

Create a test PR after implementation to verify:
- TestPyPI accepts the new version format
- Version sorts correctly
- Can be installed via pip

---

## Migration Notes

### For Existing Users

**Backward Compatibility:**
- ⚠️ This is a **breaking change** in version format
- Old versions on TestPyPI: `1.2.3rc12345`
- New versions on TestPyPI: `1.2.3.dev123045`
- Both will coexist, but `.dev` versions sort before `rc` versions

**Recommendation:**
- TestPyPI is for testing only, so breaking changes are acceptable
- Document the new format in release notes
- Users should regenerate workflows after upgrading

**Migration Steps:**
1. Upgrade `pypi-workflow-generator`
2. Regenerate workflows: `pypi-workflow-generator --python-version X.Y --test-path tests/`
3. Next PR will use new `.dev` format
4. Old `rc` versions on TestPyPI can be ignored (they're temporary test versions)

---

## Alternative: Keep "rc" Parameter Name, Change Format

If we want to avoid confusion about the `--type rc` parameter name:

### Option A: Keep parameter name, update format only
```bash
# Parameter name stays "rc" but generates .dev versions
./scripts/calculate_version.sh --type rc --bump patch --pr-number 123 --run-number 45
# Output: 1.2.4.dev123045
```
**Pro:** No parameter changes needed in workflows
**Con:** Parameter name misleading (says "rc", generates ".dev")

### Option B: Rename parameter to "dev"
```bash
# Change parameter from "rc" to "dev"
./scripts/calculate_version.sh --type dev --bump patch --pr-number 123 --run-number 45
# Output: 1.2.4.dev123045
```
**Pro:** Semantically correct parameter name
**Con:** Requires updating workflow templates

**Recommendation:** **Option A** for simplicity. The parameter name `rc` can be considered shorthand for "pre-release candidate version" which encompasses development versions.

---

## Implementation Checklist

- [ ] Update `scripts/calculate_version.sh.j2`:
  - [ ] Change version format from `rc` to `.dev`
  - [ ] Add run number padding logic (`printf -v padded_run "%03d"`)
  - [ ] Update help documentation examples
  - [ ] Update comments describing version format

- [ ] Update `README.md`:
  - [ ] Change "RC versions" to "Development versions"
  - [ ] Add "Why .dev Instead of rc?" section
  - [ ] Update all examples with new format
  - [ ] Update version format descriptions

- [ ] Add tests:
  - [ ] Test dev version format in test file
  - [ ] Test padding logic with various inputs
  - [ ] Verify script contains correct strings

- [ ] Manual testing:
  - [ ] Regenerate workflows for this project
  - [ ] Test script with small/medium/large numbers
  - [ ] Verify help output is correct

- [ ] Integration testing:
  - [ ] Create test PR
  - [ ] Verify new version format appears in workflow
  - [ ] Verify TestPyPI accepts the version
  - [ ] Verify version can be installed

- [ ] Documentation:
  - [ ] Add migration notes to CHANGELOG
  - [ ] Document version format change
  - [ ] Update any other references to version format

---

## Expected Outcomes

### Before (Current)
```
PR #123, run #45  → 1.2.3rc12345  (ambiguous)
PR #1234, run #5  → 1.2.3rc12345  (COLLISION!)
```

### After (Proposed)
```
PR #123, run #45  → 1.2.3.dev123045  (clear: PR #123, run #45)
PR #1234, run #5  → 1.2.3.dev1234005  (clear: PR #1234, run #5)
```

### Benefits
- ✅ **No ambiguity** - padding eliminates collisions
- ✅ **Semantically correct** - `.dev` versions for development
- ✅ **PEP 440 compliant** - standard Python versioning
- ✅ **Traceable** - can identify source PR from version
- ✅ **Sortable** - versions sort correctly
- ✅ **Reasonable size** - typically 6-7 digits after .dev

---

**END OF PLAN**

This plan addresses the version format issues while maintaining backward compatibility where possible and following Python packaging standards (PEP 440).
