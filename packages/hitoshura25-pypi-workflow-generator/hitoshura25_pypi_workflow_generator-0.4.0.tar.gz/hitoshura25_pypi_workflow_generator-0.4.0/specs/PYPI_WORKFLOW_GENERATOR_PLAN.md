# Implementation Plan: `pypi-workflow-generator` (v2)

This document outlines the implementation plan for a new MCP-compliant tool, `pypi-workflow-generator`, including a robust pre-release and release workflow.

## 1. Project Goal and Scope

*   **Name:** `pypi-workflow-generator`
*   **Purpose:** A command-line tool that generates a best-practice GitHub Actions workflow for testing and publishing Python packages.
*   **Scope:** The tool is intended for **general-purpose Python packaging**. It will generate a standard, high-quality workflow suitable for any Python library or application. The tool itself will be MCP-compliant in its operation.

## 2. Core Features of the Generated Workflow

The generated `.github/workflows/pypi-publish.yml` file will include:

*   **CI Triggers:** The workflow will run automatically on `pull_request` events targeting the `main` branch.
*   **Release Triggers:** The workflow will run on `push` events where a tag (e.g., `v1.0.0`) is created.
*   **Automated Testing:** It will run the project's test suite using `pytest` on every trigger.
*   **Automated Versioning:** It will use `setuptools_scm` to automatically derive the package version from Git tags.
*   **Pre-release Publishing (on PRs):** On every pull request, it will automatically build and publish a pre-release version (e.g., `1.0.1.dev5`) to the **TestPyPI** repository for testing.
*   **Production Publishing (on Tags):** When a new tag is pushed, it will build the clean release version (e.g., `1.0.1`) and publish it to the official **PyPI** repository.

## 3. Prerequisites for the Generated Workflow

Users of the generated workflow will need to configure the following secrets in their GitHub repository settings:

1.  `PYPI_API_TOKEN`: An API token for the official PyPI registry.
2.  `TEST_PYPI_API_TOKEN`: An API token for the TestPyPI registry.

## 4. Tool Architecture and Implementation

*   **Language:** Python
*   **Dual Interface:** The tool will support two modes of operation:
    1.  **CLI Mode:** For human developers, using standard `argparse` command-line flags.
    2.  **MCP Mode:** For AI agents, using a single `--mcp-input` flag that accepts a JSON payload.
*   **Templating:** It will use the Jinja2 library to render the workflow from a `pypi_publish.yml.j2` template file.

## 5. Input Parameters

*   `--python-version`: The version of Python to use in the workflow. (Default: `3.11`)
*   `--output-filename`: The name for the generated workflow file. (Default: `pypi-publish.yml`)
*   `--release-on-main-push`: A boolean flag to specify whether to initiate the release on every push to the `main` branch. (Default: `False`)

## 6. Updated CI/CD Workflow Plan

The generated `pypi-publish.yml.j2` template will contain the following logic:

```yaml
name: Build, Test, and Publish Python Package

on:
  push:
    {% if release_on_main_push %}
    branches: [ main ]
    {% else %}
    tags:
      - 'v*.*.*' # Trigger on version tags
    {% endif %}
  pull_request:
    branches: [ main ]

jobs:
  build-test-and-publish:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Required for setuptools_scm

      - name: Set up Python {{ python_version }}
        uses: actions/setup-python@v4
        with:
          python-version: '{{ python_version }}'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest twine wheel setuptools_scm

      - name: Run tests with pytest
        run: pytest

      - name: Build package
        run: python setup.py sdist bdist_wheel

      - name: Publish pre-release to TestPyPI
        if: github.event_name == 'pull_request'
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          user: __token__
          password: ${{ secrets.TEST_PYPI_API_TOKEN }}
          repository_url: https://test.pypi.org/legacy/

      - name: Publish release to PyPI
        if: github.event_name == 'push' && (startsWith(github.ref, 'refs/tags') || github.ref == 'refs/heads/main')
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          user: __token__
          password: ${{ secrets.PYPI_API_TOKEN }}
```

## 7. Release Creation Helper

To facilitate the release process when not automatically publishing on every `main` branch push, a helper script, `create_release.py`, will be included. This script will provide a simple, automatable way to create version tags.

*   **Functionality:** The script will accept a version string (e.g., `v1.0.0`) as a command-line argument. It will then execute the necessary `git` commands (`git tag <version>` and `git push origin <version>`) to create and push the tag, triggering the release workflow.
*   **Packaging:** When the project is packaged for PyPI, this script will be exposed as a console script entry point (e.g., `pypi-release`). This will allow users and AI agents to create releases with a simple command (e.g., `pypi-release v1.0.0`) after installing the package.

## 8. High-Level Development Plan

1.  **Scaffold Project:** Create a new directory `pypi-workflow-generator`.
2.  **Create Jinja2 Template:** Create the `pypi_publish.yml.j2` template file with the logic from section 6.
3.  **Implement `main.py`:** Write the core logic for the tool.
4.  **Implement `create_release.py`:** Create the helper script for manual releases.
5.  **Implement `setup.py`:** Create the `setup.py` file for this new project, including the entry point for the release helper.
6.  **"Dogfooding":** Use the newly created `pypi-workflow-generator` to generate the CI/CD workflow for itself.