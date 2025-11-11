"""Tests for the core module."""

import tempfile
from pathlib import Path

from src.dotenv_tools.core import LoadDotenv, find_dotenv_file, LoadDotenvError


class TestLoadDotenv:
    """Test loading .env files."""

    def test_load_simple(self):
        """Test loading a simple .env file."""
        content = """
        KEY1=value1
        KEY2=value2
        """

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(content)
            f.flush()

            loader = LoadDotenv(Path(f.name))
            variables = loader.load()

            assert 'KEY1' in variables
            assert 'KEY2' in variables
            assert variables['KEY1'] == 'value1'
            assert variables['KEY2'] == 'value2'

    def test_all_operators(self):
        """Test loading with all operators."""
        os_env = {}
        content = """
        A=standard
        B:=immediate
        C+=append
        D?=conditional
        """

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(content)
            f.flush()

            loader = LoadDotenv(Path(f.name))
            variables = loader.load()

            # All variables should be present
            assert 'A' in variables
            assert 'B' in variables
            assert 'C' in variables
            assert 'D' in variables

    def test_file_not_found(self):
        """Test error when file doesn't exist."""
        loader = LoadDotenv(Path('/nonexistent/.env'))

        try:
            loader.load()
            assert False, "Should have raised LoadDotenvFileNotFound"
        except LoadDotenvError:
            pass  # Expected

    def test_variable_expansion(self):
        """Test variable expansion during load."""
        os_env = {'BASE': 'test'}
        content = """
        VAR1=${BASE}/path
        VAR2=${UNDEFINED:-default}
        """

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(content)
            f.flush()

            loader = LoadDotenv(Path(f.name))
            variables = loader.load(env=os_env)

            assert variables['VAR1'] == 'test/path'
            assert variables['VAR2'] == 'default'

    def test_get_variables(self):
        """Test getting parsed variables without loading."""
        content = """
        KEY1=value1
        KEY2=value2
        """

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(content)
            f.flush()

            loader = LoadDotenv(Path(f.name))
            variables = loader.get_variables()

            assert 'KEY1' in variables
            assert 'KEY2' in variables
            assert variables['KEY1'] == ('=', 'value1')
            assert variables['KEY2'] == ('=', 'value2')


class TestFindDotenvFile:
    """Test finding .env files."""

    def test_find_in_current_dir(self):
        """Test finding .env in current directory."""
        # Create a temporary directory with .env file
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / '.env'
            env_file.write_text('TEST=value')

            # Change to that directory
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                found = find_dotenv_file()
                assert found == env_file
            finally:
                os.chdir(old_cwd)

    def test_find_in_parent_dir(self):
        """Test finding .env in parent directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / '.env'
            env_file.write_text('TEST=value')

            subdir = Path(tmpdir) / 'subdir' / 'nested'
            subdir.mkdir(parents=True)

            import os
            old_cwd = os.getcwd()
            os.chdir(subdir)

            try:
                found = find_dotenv_file()
                assert found == env_file
            finally:
                os.chdir(old_cwd)

    def test_not_found(self):
        """Test error when .env file is not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                find_dotenv_file()
                assert False, "Should have raised LoadDotenvFileNotFound"
            except LoadDotenvError:
                pass  # Expected
            finally:
                os.chdir(old_cwd)
