#!/usr/bin/env python3
"""
CLI for generating GitHub Actions release workflow.

This generates a workflow that allows users to create releases via
GitHub Actions UI, with automatic version calculation and tag creation.
"""

import argparse
import sys
from .generator import generate_release_workflow


def main():
    """Main CLI entry point for release workflow generation."""
    parser = argparse.ArgumentParser(
        description='Generate a GitHub Actions workflow for creating releases.',
        epilog="""
Examples:
  # Generate create-release.yml in .github/workflows/
  pypi-workflow-generator-release

  # Custom filename
  pypi-workflow-generator-release --output-filename my-release.yml
        """
    )

    parser.add_argument(
        '--output-filename',
        default='create-release.yml',
        help='Name for the generated workflow file (default: create-release.yml)'
    )

    args = parser.parse_args()

    try:
        result = generate_release_workflow(
            output_filename=args.output_filename
        )
        print(result['message'])
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
