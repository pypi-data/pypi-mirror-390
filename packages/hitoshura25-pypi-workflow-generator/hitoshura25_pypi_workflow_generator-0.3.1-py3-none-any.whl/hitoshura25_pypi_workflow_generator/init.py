#!/usr/bin/env python3
"""
CLI for initializing new Python projects.
"""

import argparse
import sys
from .generator import initialize_project

def main():
    """Main entry point for project initialization."""
    parser = argparse.ArgumentParser(
        description='Initialize a new Python project with PyPI publishing workflow.',
        epilog="""
Examples:
  # Auto-detect prefix from git (default)
  %(prog)s --package-name coolapp --author "Your Name" --author-email "you@example.com" \\
    --description "Cool app" --url "https://github.com/user/coolapp" --command-name coolapp

  # Use custom prefix
  %(prog)s --package-name coolapp --prefix myorg --author "..." --author-email "..." \\
    --description "..." --url "..." --command-name coolapp

  # Skip prefix
  %(prog)s --package-name coolapp --no-prefix --author "..." --author-email "..." \\
    --description "..." --url "..." --command-name coolapp
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--package-name', required=True,
                        help='Base package name (without prefix)')
    parser.add_argument('--author', required=True,
                        help='The name of the author')
    parser.add_argument('--author-email', required=True,
                        help='The email of the author')
    parser.add_argument('--description', required=True,
                        help='A short description of the package')
    parser.add_argument('--url', required=True,
                        help='The URL of the project')
    parser.add_argument('--command-name', required=True,
                        help='The name of the command-line entry point')
    parser.add_argument('--prefix', default='AUTO',
                        help='Package name prefix (default: auto-detect from git)')
    parser.add_argument('--no-prefix', action='store_true',
                        help='Skip adding prefix to package name')

    args = parser.parse_args()

    # Handle --no-prefix flag
    if args.no_prefix:
        prefix = None
    else:
        prefix = args.prefix

    try:
        result = initialize_project(
            package_name=args.package_name,
            author=args.author,
            author_email=args.author_email,
            description=args.description,
            url=args.url,
            command_name=args.command_name,
            prefix=prefix
        )

        if result['success']:
            print(result['message'])
            return 0
        else:
            print(f"Error: {result['error']}", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
