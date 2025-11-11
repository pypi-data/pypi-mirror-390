"""Core functionality for loading and unloading .env files.

This module provides the main logic for:
- Reading and parsing .env files
- Applying different assignment operators
- Expanding variables
- Loading variables into the environment
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple

from .parser import parse_file_to_dict, ParseError
from .expansion import expand_variables, expand_immediate, ExpansionError


class LoadDotenvError(Exception):
    """Base exception for load-dotenv errors."""
    pass


class LoadDotenvFileNotFound(LoadDotenvError):
    """Raised when a .env file is not found."""
    pass


class LoadDotenv:
    """Main class for loading .env files."""

    def __init__(self, env_file: Path):
        """Initialize with a .env file path.

        Args:
            env_file: Path to the .env file
        """
        self.env_file = env_file
        self.variables: Dict[str, Tuple[str, str]] = {}

    def load(self, override: bool = False, env: Dict[str, str] = None) -> Dict[str, str]:
        """Load variables from the .env file.

        Args:
            override: If True, override existing environment variables
            env: Custom environment dictionary for expansion (default: os.environ)

        Returns:
            Dictionary of loaded variables

        Raises:
            LoadDotenvFileNotFound: If the .env file doesn't exist
            LoadDotenvError: If there's an error parsing or loading
        """
        if not self.env_file.exists():
            raise LoadDotenvFileNotFound(f"File not found: {self.env_file}")

        try:
            # Read and parse the file
            content = self.env_file.read_text(encoding='utf-8')
            self.variables = parse_file_to_dict(content)
        except ParseError as e:
            raise LoadDotenvError(f"Parse error: {e}")
        except Exception as e:
            raise LoadDotenvError(f"Error reading file: {e}")

        # Environment to use for expansion
        env_dict = dict(env) if env is not None else dict(os.environ)

        # First pass: handle := (immediate expansion) and ?= (conditional)
        to_set: Dict[str, str] = {}
        to_append: Dict[str, List[str]] = {}
        deferred: Dict[str, Tuple[str, str]] = {}  # For :+= and other deferred

        for key, (op, value) in self.variables.items():
            # Skip export prefix in key
            actual_key = key[7:] if key.startswith('export ') else key

            # Get current value if exists
            current_value = env_dict.get(actual_key)

            if op == ':=':
                # Immediate expansion - expand at assignment time
                expanded = expand_immediate(value, env_dict)
                to_set[actual_key] = expanded
                env_dict[actual_key] = expanded

            elif op == '?=':
                # Conditional assignment - only if not set
                if actual_key not in env_dict or env_dict[actual_key] is None:
                    expanded = expand_variables(value, env_dict)
                    to_set[actual_key] = expanded
                    env_dict[actual_key] = expanded

            elif op == '+=':
                # Append - will handle in second pass
                to_append[actual_key] = [value]

            elif op == '=':
                # Standard assignment - deferred
                deferred[actual_key] = (op, value)

        # Second pass: handle standard = assignments with expansion
        for key, (op, value) in deferred.items():
            # Don't override unless override is True
            if not override and key in env_dict:
                continue

            expanded = expand_variables(value, env_dict)
            to_set[key] = expanded
            env_dict[key] = expanded

        # Third pass: handle += (append)
        for key, values in to_append.items():
            current = env_dict.get(key, '')
            for value in values:
                expanded = expand_immediate(value, env_dict)
                to_set[key] = current + expanded
                env_dict[key] = to_set[key]

        # Return the variables that should be set
        return to_set

    def get_variables(self) -> Dict[str, Tuple[str, str]]:
        """Get parsed variables without loading them.

        Returns:
            Dictionary of (operator, value) for each key
        """
        # Parse the file if not already parsed
        if not self.variables and self.env_file.exists():
            try:
                content = self.env_file.read_text(encoding='utf-8')
                self.variables = parse_file_to_dict(content)
            except Exception:
                # If parsing fails, return empty dict
                pass

        return self.variables


def find_dotenv_file(start_path: Path = None) -> Path:
    """Find a .env file starting from a given path.

    Searches in the following order:
    1. Current directory
    2. Parent directories (up to filesystem root)

    Args:
        start_path: Starting path for search (default: current directory)

    Returns:
        Path to the .env file

    Raises:
        LoadDotenvFileNotFound: If no .env file is found
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

    # If we get here, no .env file was found
    raise LoadDotenvFileNotFound(
        f"No .env file found starting from {start_path}"
    )
