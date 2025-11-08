"""Git utility functions."""
import subprocess
import re
from typing import Optional


def get_git_username() -> Optional[str]:
    """
    Get git username from config or remote URL.

    Tries in order:
    1. github.user (most specific)
    2. GitHub username from remote URL (more reliable)
    3. user.name (sanitized fallback)

    Returns:
        Git username or None if not found
    """
    try:
        # Try github.user first (most specific)
        result = subprocess.run(
            ['git', 'config', '--get', 'github.user'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()

        # Try extracting from GitHub remote URL
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            url = result.stdout.strip()
            # Parse https://github.com/username/repo.git
            # or git@github.com:username/repo.git
            match = re.search(r'github\.com[/:]([^/]+)/', url)
            if match:
                return match.group(1)

        # Fallback to user.name
        result = subprocess.run(
            ['git', 'config', '--get', 'user.name'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()

    except FileNotFoundError:
        # Git not installed
        pass

    return None


def sanitize_prefix(username: str) -> str:
    """
    Convert git username to valid PyPI prefix.

    Args:
        username: Raw git username

    Returns:
        Sanitized prefix suitable for PyPI

    Examples:
        >>> sanitize_prefix("John Smith")
        'john-smith'
        >>> sanitize_prefix("jsmith@company.com")
        'jsmith'
        >>> sanitize_prefix("alice_dev")
        'alice-dev'
    """
    # Lowercase
    prefix = username.lower()

    # Remove email domain if present
    if '@' in prefix:
        prefix = prefix.split('@')[0]

    # Replace invalid characters with hyphens
    prefix = re.sub(r'[^a-z0-9-]+', '-', prefix)

    # Remove leading/trailing hyphens and consecutive hyphens
    prefix = re.sub(r'-+', '-', prefix)  # Collapse multiple hyphens
    prefix = prefix.strip('-')

    return prefix


def get_default_prefix() -> str:
    """
    Get default prefix for package names.

    Auto-detects from git config. Raises error if not found.

    Returns:
        Sanitized prefix

    Raises:
        RuntimeError: If git username cannot be determined
    """
    username = get_git_username()

    if not username:
        raise RuntimeError(
            "Could not determine git username. Please either:\n"
            "  1. Configure git: git config --global github.user YOUR_USERNAME\n"
            "  2. Or provide --prefix manually: --prefix YOUR_PREFIX\n"
            "  3. Or skip prefix: --no-prefix"
        )

    prefix = sanitize_prefix(username)

    if not prefix:
        raise RuntimeError(
            f"Git username '{username}' could not be converted to valid prefix.\n"
            f"Please provide --prefix manually."
        )

    return prefix
