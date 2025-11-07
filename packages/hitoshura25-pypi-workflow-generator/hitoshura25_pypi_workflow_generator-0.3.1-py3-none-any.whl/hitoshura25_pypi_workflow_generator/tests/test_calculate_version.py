"""Tests for the calculate_version.sh script."""
import subprocess
from pathlib import Path
import pytest


def test_script_exists_after_generation(tmp_path):
    """Test that the script is generated and executable."""
    from hitoshura25_pypi_workflow_generator.generator import generate_workflows

    # Change to temp directory
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Create required files for generation
        (tmp_path / 'pyproject.toml').write_text('[build-system]')
        (tmp_path / 'setup.py').write_text('# setup')

        result = generate_workflows(
            python_version='3.11',
            test_path='tests/'
        )

        assert result['success']

        script_path = tmp_path / 'scripts' / 'calculate_version.sh'
        assert script_path.exists(), "Script file should be created"
        assert script_path.stat().st_mode & 0o111, "Script should be executable"

    finally:
        os.chdir(original_cwd)


def test_script_contains_correct_shebang(tmp_path):
    """Test that generated script has proper shebang."""
    from hitoshura25_pypi_workflow_generator.generator import generate_workflows

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

        assert content.startswith('#!/usr/bin/env bash'), "Script should have correct shebang"
        assert 'calculate_version.sh' in content, "Script should have descriptive comments"
        assert '--type' in content, "Script should accept --type argument"
        assert '--bump' in content, "Script should accept --bump argument"

    finally:
        os.chdir(original_cwd)


def test_script_directory_created(tmp_path):
    """Test that scripts directory is created."""
    from hitoshura25_pypi_workflow_generator.generator import generate_workflows

    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Create required files
        (tmp_path / 'pyproject.toml').write_text('[build-system]')
        (tmp_path / 'setup.py').write_text('# setup')

        result = generate_workflows(
            python_version='3.11',
            test_path='tests/'
        )

        assert result['success']

        scripts_dir = tmp_path / 'scripts'
        assert scripts_dir.exists(), "Scripts directory should be created"
        assert scripts_dir.is_dir(), "Scripts path should be a directory"

    finally:
        os.chdir(original_cwd)


def test_generated_files_list_includes_script(tmp_path):
    """Test that the generated files list includes the script."""
    from hitoshura25_pypi_workflow_generator.generator import generate_workflows

    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Create required files
        (tmp_path / 'pyproject.toml').write_text('[build-system]')
        (tmp_path / 'setup.py').write_text('# setup')

        result = generate_workflows(
            python_version='3.11',
            test_path='tests/'
        )

        assert result['success']
        assert len(result['files_created']) == 4, "Should create 3 workflow files + 1 script"

        # Check that script is in the list
        files_str = str(result['files_created'])
        assert 'calculate_version.sh' in files_str, "Script should be in generated files list"

    finally:
        os.chdir(original_cwd)


def test_script_uses_dev_format(tmp_path):
    """Test that the script generates .dev versions instead of rc."""
    from hitoshura25_pypi_workflow_generator.generator import generate_workflows

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

        # Should use .dev instead of rc in version generation
        assert '.dev' in content, "Script should generate .dev versions"
        assert 'Generated dev version' in content, "Script should mention dev version in output"

        # Should have padding logic
        assert 'printf -v padded_run "%03d"' in content, "Script should pad run numbers to 3 digits"

        # Help should show dev examples
        assert '1.2.4.dev123045' in content, "Help should show .dev version example"

    finally:
        os.chdir(original_cwd)


def test_script_help_shows_dev_format(tmp_path):
    """Test that script help documentation shows development version format."""
    from hitoshura25_pypi_workflow_generator.generator import generate_workflows

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

        # Check help examples show development versions
        assert 'Development version for PR' in content, "Help should describe development versions"
        assert '1.2.4.dev123045' in content, "Help should show .dev version example"

    finally:
        os.chdir(original_cwd)
