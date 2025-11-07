#!/usr/bin/env python3
"""
CLI for creating git release tags.
"""

import argparse
import subprocess
import sys
from .generator import create_git_release

def create_release_tag_with_overwrite(version, overwrite=False):
    """
    Create a git release tag with optional overwrite.

    Args:
        version: Version tag to create
        overwrite: Whether to overwrite existing tag

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    tag_exists = False
    try:
        # Check if the tag already exists
        subprocess.run(['git', 'rev-parse', version], check=True, capture_output=True)
        tag_exists = True
    except subprocess.CalledProcessError:
        # The tag does not exist, so we can proceed
        pass

    if tag_exists:
        if overwrite:
            print(f"Tag {version} already exists. Overwriting.")
            try:
                subprocess.run(['git', 'tag', '-d', version], check=True)
                try:
                    subprocess.run(['git', 'push', 'origin', ':' + version], check=True)
                except subprocess.CalledProcessError:
                    # The remote tag does not exist, which is fine
                    pass
            except subprocess.CalledProcessError as e:
                print(f"Error deleting tag: {e}", file=sys.stderr)
                return 1
        else:
            print(f"Error: Tag {version} already exists. Use --overwrite to replace it.", file=sys.stderr)
            return 1

    # Use shared generator function
    result = create_git_release(version)
    print(result['message'])
    return 0 if result['success'] else 1


def main():
    """Main entry point for creating releases."""
    parser = argparse.ArgumentParser(description='Create and push a git version tag.')
    parser.add_argument('release_type', choices=['major', 'minor', 'patch'], help='The type of release (major, minor, or patch).')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite an existing tag.')
    args = parser.parse_args()

    try:
        latest_tag = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], check=True, capture_output=True, text=True).stdout.strip()
        major, minor, patch = map(int, latest_tag.lstrip('v').split('.'))
    except (subprocess.CalledProcessError, ValueError):
        major, minor, patch = 0, 0, 0

    if args.release_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif args.release_type == 'minor':
        minor += 1
        patch = 0
    elif args.release_type == 'patch':
        patch += 1

    new_version = f'v{major}.{minor}.{patch}'

    return create_release_tag_with_overwrite(new_version, args.overwrite)

if __name__ == "__main__":
    sys.exit(main())
