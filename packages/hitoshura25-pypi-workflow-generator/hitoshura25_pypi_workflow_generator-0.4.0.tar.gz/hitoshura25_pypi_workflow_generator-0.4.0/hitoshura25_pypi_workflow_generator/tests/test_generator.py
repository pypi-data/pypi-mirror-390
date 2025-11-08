import os
from hitoshura25_pypi_workflow_generator.generator import generate_workflows

def test_generate_workflows_default_arguments(tmp_path):
    """Test workflow generation with default arguments."""
    # Create dummy project files required for validation
    (tmp_path / 'pyproject.toml').write_text('[build-system]')
    (tmp_path / 'setup.py').write_text('from setuptools import setup\nsetup()')

    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        output_dir = tmp_path / ".github" / "workflows"
        result = generate_workflows(
            python_version='3.11',
            test_path='.',
            base_output_dir=output_dir,
            verbose_publish=False
        )

        assert result['success']
        assert 'files_created' in result
        assert 'message' in result
        assert len(result['files_created']) == 4  # 3 workflows + 1 script

        # Verify all 3 workflow files exist
        reusable_file = output_dir / '_reusable-test-build.yml'
        release_file = output_dir / 'release.yml'
        test_pr_file = output_dir / 'test-pr.yml'

        assert reusable_file.exists()
        assert release_file.exists()
        assert test_pr_file.exists()

        # Verify script file exists and is executable
        script_file = tmp_path / 'scripts' / 'calculate_version.sh'
        assert script_file.exists()
        assert script_file.stat().st_mode & 0o111  # Check executable bit

        # Check reusable workflow content
        with open(reusable_file, 'r') as f:
            content = f.read()

        assert "python-version: '3.11'" in content or "python_version" in content
        assert "pytest" in content

    finally:
        os.chdir(original_cwd)


def test_generate_workflows_custom_arguments(tmp_path):
    """Test workflow generation with custom arguments."""
    # Create dummy project files required for validation
    (tmp_path / 'pyproject.toml').write_text('[build-system]')
    (tmp_path / 'setup.py').write_text('from setuptools import setup\nsetup()')

    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        output_dir = tmp_path / ".github" / "workflows"
        result = generate_workflows(
            python_version='3.9',
            test_path='tests',
            base_output_dir=output_dir,
            verbose_publish=True
        )

        assert result['success']
        assert 'files_created' in result
        assert 'message' in result
        assert len(result['files_created']) == 4  # 3 workflows + 1 script

        # Verify all 3 workflow files exist
        reusable_file = output_dir / '_reusable-test-build.yml'
        release_file = output_dir / 'release.yml'
        test_pr_file = output_dir / 'test-pr.yml'

        assert reusable_file.exists()
        assert release_file.exists()
        assert test_pr_file.exists()

        # Verify script file exists and is executable
        script_file = tmp_path / 'scripts' / 'calculate_version.sh'
        assert script_file.exists()
        assert script_file.stat().st_mode & 0o111  # Check executable bit

        # Check custom Python version in reusable workflow
        with open(reusable_file, 'r') as f:
            reusable_content = f.read()

        assert "3.9" in reusable_content
        # Verify test_path is actually used in pytest command
        assert "pytest" in reusable_content
        assert "${{ inputs.test_path }}" in reusable_content or "pytest tests" in reusable_content

        # Check verbose publish in test-pr workflow (where publishing happens now)
        with open(test_pr_file, 'r') as f:
            test_pr_content = f.read()

        assert "verbose: true" in test_pr_content

    finally:
        os.chdir(original_cwd)