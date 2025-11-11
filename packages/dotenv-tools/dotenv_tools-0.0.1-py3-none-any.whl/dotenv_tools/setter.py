"""SetDotenv: Class for setting, updating, and removing environment variables in .env files.

This module provides functionality to:
- Set individual environment variables
- Remove variables from .env files
- Edit .env files with custom editor
- Update existing variables
"""

import os
import re
from pathlib import Path
from typing import Optional, List, Tuple


class SetDotenvError(Exception):
    """Base exception for set-dotenv errors."""
    pass


class SetDotenvFileNotFound(SetDotenvError):
    """Raised when a .env file is not found."""
    pass


class SetDotenv:
    """Main class for setting variables in .env files."""

    def __init__(self, env_file: Path):
        """Initialize with a .env file path.

        Args:
            env_file: Path to the .env file
        """
        self.env_file = env_file

    def set_variable(self, key: str, value: str, operator: str = '=') -> None:
        """Set a variable in the .env file.

        Args:
            key: Environment variable name
            value: Value to set
            operator: Assignment operator (=, :=, +=, ?=)

        Raises:
            SetDotenvError: If there's an error writing to file
        """
        # Validate key
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key):
            raise SetDotenvError(f"Invalid environment variable name: {key}")

        # Read existing file or create new
        lines = self._read_lines()

        # Find if key already exists
        key_pattern = re.compile(rf'^\s*(?:export\s+)?{re.escape(key)}\s*([+?:]?=)')

        for i, line in enumerate(lines):
            if key_pattern.match(line):
                # Update existing line
                new_line = self._format_line(key, value, operator, line)
                lines[i] = new_line
                self._write_lines(lines)
                return

        # Key doesn't exist, append new line
        new_line = self._format_line(key, value, operator)
        lines.append(new_line)
        self._write_lines(lines)

    def remove_variable(self, key: str) -> bool:
        """Remove a variable from the .env file.

        Args:
            key: Environment variable name to remove

        Returns:
            True if variable was removed, False if it didn't exist

        Raises:
            SetDotenvError: If there's an error writing to file
        """
        # Read existing file
        lines = self._read_lines()

        # Find and remove key
        key_pattern = re.compile(rf'^\s*(?:export\s+)?{re.escape(key)}\s*[+?:]?=.*$')

        # Check if any line matches before removing
        removed = any(key_pattern.match(line) for line in lines)

        # Remove matching lines
        lines = [line for line in lines if not key_pattern.match(line)]
        self._write_lines(lines)

        return removed

    def get_variable(self, key: str) -> Optional[Tuple[str, str]]:
        """Get a variable from the .env file.

        Args:
            key: Environment variable name

        Returns:
            Tuple of (operator, value) or None if not found

        Raises:
            SetDotenvError: If there's an error reading file
        """
        try:
            if not self.env_file.exists():
                return None

            content = self.env_file.read_text(encoding='utf-8')
            lines = content.split('\n')

            key_pattern = re.compile(rf'^\s*(?:export\s+)?{re.escape(key)}\s*([+?:]?=)\s*(.*)$')

            for line in lines:
                match = key_pattern.match(line)
                if match:
                    operator = match.group(1)
                    value = match.group(2).strip()
                    return (operator, value)

            return None
        except Exception as e:
            raise SetDotenvError(f"Error reading file: {e}")

    def list_variables(self) -> List[Tuple[str, str, str]]:
        """List all variables in the .env file.

        Returns:
            List of (key, operator, value) tuples

        Raises:
            SetDotenvError: If there's an error reading file
        """
        try:
            if not self.env_file.exists():
                return []

            content = self.env_file.read_text(encoding='utf-8')
            lines = content.split('\n')

            variables = []
            # Pattern to match KEY=VALUE, KEY:=VALUE, KEY+=VALUE, KEY?=VALUE
            pattern = re.compile(r'^\s*(?:export\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*([+?:]?=)\s*(.*)$')

            for line in lines:
                match = pattern.match(line)
                if match:
                    key = match.group(1)
                    operator = match.group(2)
                    value = match.group(3).strip()
                    variables.append((key, operator, value))

            return variables
        except Exception as e:
            raise SetDotenvError(f"Error reading file: {e}")

    def _read_lines(self) -> List[str]:
        """Read lines from the .env file.

        Returns:
            List of lines

        Raises:
            SetDotenvFileNotFound: If file doesn't exist and create_if_missing is False
        """
        if not self.env_file.exists():
            return []

        try:
            content = self.env_file.read_text(encoding='utf-8')
            return content.split('\n')
        except Exception as e:
            raise SetDotenvError(f"Error reading file: {e}")

    def _write_lines(self, lines: List[str]) -> None:
        """Write lines to the .env file.

        Args:
            lines: List of lines to write

        Raises:
            SetDotenvError: If there's an error writing to file
        """
        try:
            # Ensure parent directory exists
            self.env_file.parent.mkdir(parents=True, exist_ok=True)

            # Write with newline at end
            content = '\n'.join(lines)
            if content and not content.endswith('\n'):
                content += '\n'

            self.env_file.write_text(content, encoding='utf-8')
        except Exception as e:
            raise SetDotenvError(f"Error writing file: {e}")

    def _format_line(self, key: str, value: str, operator: str, original_line: str = None) -> str:
        """Format a line for the .env file.

        Args:
            key: Environment variable name
            value: Value to set
            operator: Assignment operator
            original_line: Original line (if updating)

        Returns:
            Formatted line
        """
        # Preserve export prefix if present in original
        export_prefix = ""
        if original_line:
            if re.match(r'^\s*export\s+', original_line):
                export_prefix = "export "

        # Standard dotenv format: no spaces around operator
        return f"{export_prefix}{key}{operator}{value}"

    def edit_file(self, editor: Optional[str] = None) -> None:
        """Edit the .env file using a text editor.

        Args:
            editor: Editor to use (default: $EDITOR or $VISUAL)

        Raises:
            SetDotenvError: If editor is not available
        """
        # Get editor
        if editor is None:
            editor = os.environ.get('VISUAL') or os.environ.get('EDITOR', 'vi')

        # Check if file exists
        if not self.env_file.exists():
            # Create empty file
            self.env_file.touch()

        # Check if editor exists
        if not os.path.exists(editor):
            raise SetDotenvError(
                f"Editor '{editor}' not found. Set $EDITOR or use --editor option."
            )

        # Launch editor
        import subprocess
        try:
            subprocess.run([editor, str(self.env_file)], check=True)
        except subprocess.CalledProcessError as e:
            raise SetDotenvError(f"Editor exited with error: {e}")
        except Exception as e:
            raise SetDotenvError(f"Error launching editor: {e}")


def find_or_create_dotenv_file(start_path: Path = None) -> Path:
    """Find or create a .env file.

    Searches for existing .env file, or creates one in the current directory.

    Args:
        start_path: Starting path for search (default: current directory)

    Returns:
        Path to the .env file (created if not exists)

    Raises:
        SetDotenvError: If there's an error creating file
    """
    if start_path is None:
        start_path = Path.cwd()

    start_path = Path(start_path).resolve()
    current = start_path

    # Search current directory and parents
    for path in [current] + list(current.parents):
        env_file = path / '.env'
        if env_file.exists():
            return env_file

    # If we get here, no .env file was found - create one in current directory
    env_file = current / '.env'
    try:
        env_file.touch()
        return env_file
    except Exception as e:
        raise SetDotenvError(f"Error creating .env file: {e}")
