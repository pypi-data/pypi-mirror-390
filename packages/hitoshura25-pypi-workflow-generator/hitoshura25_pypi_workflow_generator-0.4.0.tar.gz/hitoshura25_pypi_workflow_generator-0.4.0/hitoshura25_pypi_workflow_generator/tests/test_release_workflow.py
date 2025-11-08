"""
Tests for release workflow generation.
"""
import os
from pathlib import Path
from hitoshura25_pypi_workflow_generator.generator import generate_workflows


def test_release_workflow_structure(tmp_path: Path):
    """Test that release workflow has correct structure."""
    # Create dummy pyproject.toml and setup.py for validation
    (tmp_path / 'pyproject.toml').write_text('[build-system]')
    (tmp_path / 'setup.py').write_text('from setuptools import setup\nsetup()')

    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        output_dir = tmp_path / ".github" / "workflows"
        result = generate_workflows(
            python_version='3.11',
            base_output_dir=str(output_dir)
        )

        assert result['success']
        assert 'files_created' in result

        # Verify release workflow exists
        output_file = output_dir / 'release.yml'
        assert output_file.exists()

        with open(output_file, 'r') as f:
            content = f.read()

        # Verify workflow structure
        assert "name: Release to PyPI" in content or "Release" in content
        assert "workflow_dispatch" in content
        assert "release_type" in content
        assert "patch" in content
        assert "minor" in content
        assert "major" in content

    finally:
        os.chdir(original_cwd)


def test_workflows_creates_directory(tmp_path: Path):
    """Test that workflow generation creates output directory if needed."""
    # Create dummy pyproject.toml and setup.py for validation
    (tmp_path / 'pyproject.toml').write_text('[build-system]')
    (tmp_path / 'setup.py').write_text('from setuptools import setup\nsetup()')

    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        output_dir = tmp_path / ".github" / "workflows"
        assert not output_dir.exists()

        result = generate_workflows(
            base_output_dir=str(output_dir)
        )

        assert result['success']
        assert output_dir.exists()
        assert (output_dir / 'release.yml').exists()

    finally:
        os.chdir(original_cwd)


def test_generate_workflows_includes_all_three_files(tmp_path: Path):
    """Test that generate_workflows creates all 3 workflow files."""
    # Create dummy pyproject.toml and setup.py for validation
    (tmp_path / 'pyproject.toml').write_text('[build-system]')
    (tmp_path / 'setup.py').write_text('from setuptools import setup\nsetup()')

    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        output_dir = tmp_path / ".github" / "workflows"
        result = generate_workflows(
            python_version='3.11',
            base_output_dir=str(output_dir)
        )

        assert result['success']
        assert 'files_created' in result
        assert len(result['files_created']) == 4  # 3 workflows + 1 script

        # All 3 workflows should exist
        assert (output_dir / '_reusable-test-build.yml').exists()
        assert (output_dir / 'release.yml').exists()
        assert (output_dir / 'test-pr.yml').exists()

        # Script should exist
        assert (tmp_path / 'scripts' / 'calculate_version.sh').exists()

    finally:
        os.chdir(original_cwd)
