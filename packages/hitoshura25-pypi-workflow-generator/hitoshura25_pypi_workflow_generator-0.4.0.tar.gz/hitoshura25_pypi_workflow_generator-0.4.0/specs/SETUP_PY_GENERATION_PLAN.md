## Implementation Plan: Extend `pypi-workflow-generator` for `setup.py` Generation

### 1. Project Goal:
Extend `pypi-workflow-generator` to assist users in configuring their Python project's packaging metadata (`setup.py`) to be compatible with the generated GitHub Actions workflow, especially regarding automated versioning and PyPI publishing best practices.

### 2. Scope:
The initial scope will focus on generating a `setup.py` file. Support for `pyproject.toml` (PEP 621) can be a future enhancement.

### 3. Core Features:
*   **Generate `setup.py`:** The tool will be able to generate a new `setup.py` file for a user's project.
*   **Include `setuptools_scm`:** The generated `setup.py` will automatically include `use_scm_version=True` and `setup_requires=['setuptools_scm']`.
*   **Build System Compatibility:** The generated `setup.py` will be compatible with `python -m build` (PEP 517/518 compliant).
*   **Recommended Dependencies:** The plan will implicitly recommend `build` as a dependency for building.
*   **Dynamic `long_description`:** The generated `setup.py` will dynamically read `long_description` from `README.md`.
*   **Basic Metadata:** Include placeholders for `name`, `author`, `author_email`, `description`, `url`, `license`, and `classifiers`.
*   **`find_packages()`:** Use `find_packages()` for package discovery.
*   **`install_requires`:** Include a placeholder for project dependencies.
*   **CLI/MCP Integration:** The new functionality will be accessible via both CLI and MCP modes.

### 4. Modifications to `pypi_workflow_generator`:
*   **New Jinja2 Template (`setup.py.j2`):** Create a new Jinja2 template for the `setup.py` file. This template will contain the structure and placeholders for the `setup.py` content.
*   **Update `main.py`:**
    *   **New Argument Parsing:** Add new arguments to `argparse` for `setup.py` generation. This might include a flag like `--generate-setup-py` and options for project name, author, etc.
    *   **New MCP Input:** Extend the `--mcp-input` JSON schema to include parameters for `setup.py` generation.
    *   **New Function (`generate_setup_py`):** Implement a new function similar to `generate_workflow` that takes `setup.py` parameters, renders `setup.py.j2`, and writes it to the project root.
    *   **Integration:** Call `generate_setup_py` when the appropriate arguments are provided.

### 5. Input Parameters (New):
*   `--generate-setup-py`: A boolean flag to trigger `setup.py` generation (default: `False`).
*   `--project-name`: The name of the Python package (e.g., `my-awesome-package`).
*   `--author`: The author's name.
*   `--author-email`: The author's email.
*   `--description`: A short description of the package.
*   `--url`: The project's homepage URL.
*   `--license`: The project's license (e.g., `MIT`).
*   `--dependencies`: A comma-separated list of initial dependencies (e.g., `requests,numpy`).

### 6. Updated CI/CD Workflow (No direct changes to `pypi-publish.yml.j2`):
The generated `pypi-publish.yml` will remain focused on building and publishing. The new `setup.py` generation will be a separate function of the tool.

### 7. Testing:
*   **Unit Tests for `generate_setup_py`:**
    *   Test generation with default parameters.
    *   Test generation with custom parameters.
    *   Verify that `setuptools_scm` is correctly configured.
    *   Verify that `long_description` is read dynamically.
    *   Use `tmp_path` for output to avoid file system side effects.
*   **Integration Tests:** (Optional, more complex) Test the full flow of generating both the workflow and `setup.py`.

### 8. Documentation:
*   Update the top-level `README.md` to describe the new `setup.py` generation feature.
*   Update `pypi_workflow_generator/README.md` to reflect the new functionality.

### 9. High-Level Development Plan:
1.  Create `setup.py.j2` template.
2.  Implement `generate_setup_py` function in `main.py`.
3.  Add argument parsing for `setup.py` generation in `main.py`.
4.  Implement unit tests for `generate_setup_py`.
5.  Update documentation.
