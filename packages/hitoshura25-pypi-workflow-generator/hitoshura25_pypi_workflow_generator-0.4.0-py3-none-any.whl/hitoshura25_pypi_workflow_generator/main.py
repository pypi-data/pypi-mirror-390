#!/usr/bin/env python3
"""
CLI for PyPI Workflow Generator.

This module provides the command-line interface for generating
GitHub Actions workflows.
"""

import argparse
import sys
from .generator import generate_workflows

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="""
Generate GitHub Actions workflows for automated PyPI publishing.

Generates 3 workflow files:
  - _reusable-test-build.yml (shared test/build logic)
  - release.yml (manual releases via GitHub UI)
  - test-pr.yml (PR testing to TestPyPI)

Benefits:
  - No PAT or GitHub App tokens required
  - Test/build before pushing tags (safe failure handling)
  - DRY: shared logic for build/test/publish
  - Simple per-repository setup (only PyPI Trusted Publisher needed)

Example:
  pypi-workflow-generator --python-version 3.11 --verbose-publish

This creates:
  .github/workflows/_reusable-test-build.yml
  .github/workflows/release.yml
  .github/workflows/test-pr.yml
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--python-version',
        default='3.11',
        help='Python version to use in workflows (default: 3.11)'
    )
    parser.add_argument(
        '--test-path',
        default='.',
        help='Path to tests directory (default: .)'
    )
    parser.add_argument(
        '--verbose-publish',
        action='store_true',
        help='Enable verbose mode for PyPI publishing actions'
    )

    args = parser.parse_args()

    try:
        result = generate_workflows(
            python_version=args.python_version,
            test_path=args.test_path,
            verbose_publish=args.verbose_publish
        )
        print(result['message'])
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nHint: Run 'pypi-workflow-generator-init' to initialize your project first.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
