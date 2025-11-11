"""Tests for the CLI module."""

import os
import tempfile
from pathlib import Path
from click.testing import CliRunner
from src.dotenv_tools.cli import cli


class TestCLI:
    """Test CLI commands."""

    def test_load_dotenv_no_args(self):
        """Test load-dotenv without arguments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / '.env'
            env_file.write_text('KEY1=value1\nKEY2=value2')

            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                runner = CliRunner()
                result = runner.invoke(cli, ['load-dotenv'])

                assert result.exit_code == 0
                assert 'Successfully loaded' in result.output

                # Check variables are loaded
                assert os.environ['KEY1'] == 'value1'
                assert os.environ['KEY2'] == 'value2'
            finally:
                os.chdir(old_cwd)

    def test_load_dotenv_with_file(self):
        """Test load-dotenv with explicit file path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('TEST_VAR=test_value\n')
            f.flush()

            runner = CliRunner()
            result = runner.invoke(cli, ['load-dotenv', f.name])

            assert result.exit_code == 0
            assert 'Successfully loaded' in result.output
            assert os.environ['TEST_VAR'] == 'test_value'

    def test_unload_dotenv(self):
        """Test unload-dotenv command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # First load
                env_file = Path(tmpdir) / '.env'
                env_file.write_text('VAR1=value1')

                runner = CliRunner()
                result = runner.invoke(cli, ['load-dotenv'])
                assert result.exit_code == 0

                # Then unload
                result = runner.invoke(cli, ['unload-dotenv', '--force'])
                assert result.exit_code == 0
                assert 'Successfully unloaded' in result.output
                assert 'VAR1' not in os.environ
            finally:
                os.chdir(old_cwd)

    def test_verbose_flag(self):
        """Test verbose flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                env_file = Path(tmpdir) / '.env'
                env_file.write_text('KEY1=value1')

                runner = CliRunner()
                result = runner.invoke(cli, ['load-dotenv', '--verbose'])

                assert result.exit_code == 0
                assert 'KEY1 = value1' in result.output
            finally:
                os.chdir(old_cwd)

    def test_file_not_found(self):
        """Test error when file is not found."""
        runner = CliRunner()
        result = runner.invoke(cli, ['load-dotenv', '/nonexistent/file.env'])

        assert result.exit_code != 0
        assert 'File not found' in result.output
