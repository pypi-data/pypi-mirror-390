"""Tests for git utility functions."""
import pytest
from unittest.mock import patch, MagicMock
from hitoshura25_pypi_workflow_generator.git_utils import (
    get_git_username,
    sanitize_prefix,
    get_default_prefix
)


def test_sanitize_prefix_simple():
    """Test sanitizing simple usernames."""
    assert sanitize_prefix("jsmith") == "jsmith"
    assert sanitize_prefix("alice") == "alice"


def test_sanitize_prefix_with_spaces():
    """Test sanitizing names with spaces."""
    assert sanitize_prefix("John Smith") == "john-smith"
    assert sanitize_prefix("Alice Bob") == "alice-bob"


def test_sanitize_prefix_with_email():
    """Test sanitizing email addresses."""
    assert sanitize_prefix("jsmith@example.com") == "jsmith"
    assert sanitize_prefix("alice@company.org") == "alice"


def test_sanitize_prefix_with_special_chars():
    """Test sanitizing names with special characters."""
    assert sanitize_prefix("alice_dev") == "alice-dev"
    assert sanitize_prefix("bob's_packages") == "bob-s-packages"  # Apostrophe replaced with hyphen
    assert sanitize_prefix("user#123") == "user-123"


def test_sanitize_prefix_consecutive_hyphens():
    """Test collapsing consecutive hyphens."""
    assert sanitize_prefix("alice---bob") == "alice-bob"
    assert sanitize_prefix("test--name") == "test-name"


def test_sanitize_prefix_uppercase():
    """Test converting uppercase to lowercase."""
    assert sanitize_prefix("ALICE") == "alice"
    assert sanitize_prefix("John-Smith") == "john-smith"


@patch('subprocess.run')
def test_get_git_username_github_user(mock_run):
    """Test getting username from github.user."""
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="jsmith\n"
    )
    assert get_git_username() == "jsmith"
    # Should call git config --get github.user
    mock_run.assert_called_once()
    assert 'github.user' in str(mock_run.call_args)


@patch('subprocess.run')
def test_get_git_username_from_remote_url_ssh(mock_run):
    """Test extracting username from SSH remote URL."""
    def side_effect(*args, **kwargs):
        cmd = args[0]
        if 'github.user' in cmd:
            return MagicMock(returncode=1, stdout="")
        elif 'remote' in cmd and 'get-url' in cmd:
            return MagicMock(returncode=0, stdout="git@github.com:hitoshura25/pypi-workflow-generator.git\n")
        elif 'user.name' in cmd:
            return MagicMock(returncode=1, stdout="")
        return MagicMock(returncode=1, stdout="")

    mock_run.side_effect = side_effect
    assert get_git_username() == "hitoshura25"


@patch('subprocess.run')
def test_get_git_username_from_remote_url_https(mock_run):
    """Test extracting username from HTTPS remote URL."""
    def side_effect(*args, **kwargs):
        cmd = args[0]
        if 'github.user' in cmd:
            return MagicMock(returncode=1, stdout="")
        elif 'remote' in cmd and 'get-url' in cmd:
            return MagicMock(returncode=0, stdout="https://github.com/jsmith/my-repo.git\n")
        elif 'user.name' in cmd:
            return MagicMock(returncode=1, stdout="")
        return MagicMock(returncode=1, stdout="")

    mock_run.side_effect = side_effect
    assert get_git_username() == "jsmith"


@patch('subprocess.run')
def test_get_git_username_fallback_to_user_name(mock_run):
    """Test fallback to user.name when github.user and remote not set."""
    def side_effect(*args, **kwargs):
        cmd = args[0]
        if 'github.user' in cmd:
            return MagicMock(returncode=1, stdout="")
        elif 'remote' in cmd and 'get-url' in cmd:
            return MagicMock(returncode=1, stdout="")
        elif 'user.name' in cmd:
            return MagicMock(returncode=0, stdout="John Smith\n")
        return MagicMock(returncode=1, stdout="")

    mock_run.side_effect = side_effect
    assert get_git_username() == "John Smith"


@patch('subprocess.run')
def test_get_git_username_not_configured(mock_run):
    """Test when git is not configured."""
    mock_run.return_value = MagicMock(returncode=1, stdout="")
    assert get_git_username() is None


@patch('subprocess.run')
def test_get_git_username_git_not_installed(mock_run):
    """Test when git is not installed."""
    mock_run.side_effect = FileNotFoundError()
    assert get_git_username() is None


@patch('subprocess.run')
def test_get_default_prefix_success(mock_run):
    """Test successful prefix detection."""
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="jsmith\n"
    )
    assert get_default_prefix() == "jsmith"


@patch('subprocess.run')
def test_get_default_prefix_failure(mock_run):
    """Test failure when git not configured."""
    mock_run.return_value = MagicMock(returncode=1, stdout="")

    with pytest.raises(RuntimeError, match="Could not determine git username"):
        get_default_prefix()


@patch('subprocess.run')
def test_get_default_prefix_with_sanitization(mock_run):
    """Test that get_default_prefix sanitizes the username."""
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="John Smith\n"
    )
    assert get_default_prefix() == "john-smith"


@patch('subprocess.run')
def test_get_default_prefix_empty_after_sanitization(mock_run):
    """Test error when username becomes empty after sanitization."""
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="---\n"  # Only special chars that get removed
    )

    with pytest.raises(RuntimeError, match="could not be converted to valid prefix"):
        get_default_prefix()
