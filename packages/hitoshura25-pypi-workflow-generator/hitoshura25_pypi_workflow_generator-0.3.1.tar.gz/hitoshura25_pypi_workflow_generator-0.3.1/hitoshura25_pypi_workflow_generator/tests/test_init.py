import os
from unittest.mock import patch
from hitoshura25_pypi_workflow_generator.generator import initialize_project

def test_init_project(tmp_path):
    """Test project initialization without prefix."""
    # Change the current working directory to the temporary directory
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        # Run the initialize_project function with no prefix
        result = initialize_project(
            package_name='my-package',
            author='My Name',
            author_email='my.email@example.com',
            description='My new package.',
            url='https://github.com/my-username/my-package',
            command_name='my-command',
            prefix=None  # Skip prefix
        )

        # Assert the function returned success
        assert result['success']
        assert 'files_created' in result
        assert 'message' in result
        assert result['package_name'] == 'my-package'
        assert result['import_name'] == 'my_package'

        # Assert that the files have been created
        assert os.path.exists('pyproject.toml')
        assert os.path.exists('setup.py')
        assert os.path.exists('my_package/__init__.py')
        assert os.path.exists('my_package/main.py')

        # Assert that the contents of the files are correct
        with open('pyproject.toml', 'r') as f:
            pyproject_content = f.read()
        assert "[build-system]" in pyproject_content
        assert "requires = [\"setuptools>=61.0\", \"setuptools_scm[toml]>=6.2\"]" in pyproject_content
        assert "build-backend = \"setuptools.build_meta\"" in pyproject_content
        assert "[tool.setuptools_scm]" in pyproject_content
        assert "version_scheme = \"post-release\"" in pyproject_content

        with open('setup.py', 'r') as f:
            setup_content = f.read()
        assert "name='my-package'," in setup_content
        assert "author='My Name'," in setup_content
        assert "author_email='my.email@example.com'," in setup_content
        assert "description='My new package.'," in setup_content
        assert "url='https://github.com/my-username/my-package'," in setup_content
        assert "'my-command=my_package.main:main'," in setup_content

    finally:
        os.chdir(original_cwd)


@patch('hitoshura25_pypi_workflow_generator.git_utils.get_git_username')
def test_init_with_auto_prefix(mock_git, tmp_path):
    """Test initialization with auto-detected prefix."""
    mock_git.return_value = "jsmith"

    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        result = initialize_project(
            package_name="coolapp",
            author="John Smith",
            author_email="john@example.com",
            description="Cool app",
            url="https://github.com/jsmith/coolapp",
            command_name="coolapp",
            prefix="AUTO"
        )

        assert result['success']
        assert result['package_name'] == "jsmith-coolapp"
        assert result['import_name'] == "jsmith_coolapp"
        assert result['prefix'] == "jsmith"

        # Check directory created
        assert os.path.exists("jsmith_coolapp")
        assert os.path.exists("jsmith_coolapp/__init__.py")
        assert os.path.exists("jsmith_coolapp/main.py")

        # Check setup.py has correct name
        with open('setup.py', 'r') as f:
            setup_content = f.read()
        assert "name='jsmith-coolapp'" in setup_content or 'name="jsmith-coolapp"' in setup_content

    finally:
        os.chdir(original_cwd)


def test_init_with_custom_prefix(tmp_path):
    """Test initialization with custom prefix."""
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        result = initialize_project(
            package_name="coolapp",
            author="Acme Corp",
            author_email="dev@acme.com",
            description="Cool app",
            url="https://github.com/acme/coolapp",
            command_name="coolapp",
            prefix="myorg"
        )

        assert result['success']
        assert result['package_name'] == "myorg-coolapp"
        assert result['import_name'] == "myorg_coolapp"
        assert result['prefix'] == "myorg"

        # Check directory created
        assert os.path.exists("myorg_coolapp")

        # Check setup.py has correct name
        with open('setup.py', 'r') as f:
            setup_content = f.read()
        assert "name='myorg-coolapp'" in setup_content or 'name="myorg-coolapp"' in setup_content

    finally:
        os.chdir(original_cwd)


def test_init_with_no_prefix(tmp_path):
    """Test initialization without prefix."""
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        result = initialize_project(
            package_name="coolapp",
            author="Dev",
            author_email="dev@example.com",
            description="Cool app",
            url="https://github.com/dev/coolapp",
            command_name="coolapp",
            prefix=None
        )

        assert result['success']
        assert result['package_name'] == "coolapp"
        assert result['import_name'] == "coolapp"
        assert result['prefix'] is None

        # Check directory created
        assert os.path.exists("coolapp")

        # Check setup.py has correct name
        with open('setup.py', 'r') as f:
            setup_content = f.read()
        assert "name='coolapp'" in setup_content or 'name="coolapp"' in setup_content

    finally:
        os.chdir(original_cwd)


@patch('hitoshura25_pypi_workflow_generator.git_utils.get_git_username')
def test_init_auto_prefix_fails_when_git_not_configured(mock_git, tmp_path):
    """Test that AUTO prefix fails gracefully when git not configured."""
    mock_git.return_value = None

    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        result = initialize_project(
            package_name="coolapp",
            author="Dev",
            author_email="dev@example.com",
            description="Cool app",
            url="https://github.com/dev/coolapp",
            command_name="coolapp",
            prefix="AUTO"
        )

        assert not result['success']
        assert 'error' in result
        assert "Could not determine git username" in result['error']

    finally:
        os.chdir(original_cwd)
