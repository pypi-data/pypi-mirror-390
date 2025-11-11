"""Track environment variables for load/unload operations.

This module provides functionality to:
- Snapshot the current environment state
- Track which variables were loaded by load-dotenv
- Persist tracking information across CLI invocations
- Restore environment by unloading tracked variables
"""

import os
import json
import stat
from pathlib import Path
from typing import Dict, Set, Optional, Tuple


class Tracker:
    """Track environment variables loaded by load-dotenv."""

    def __init__(self, state_file: Path):
        """Initialize the tracker.

        Args:
            state_file: Path to the state file for persistence
        """
        self.state_file = state_file
        self.loaded_vars: Set[str] = set()
        self.original_values: Dict[str, Optional[str]] = {}

    def snapshot_environment(self) -> None:
        """Capture the current environment state.

        This should be called before loading new variables.
        """
        self.original_values = dict(os.environ)

    def load_variables(self, variables: Dict[str, str]) -> int:
        """Load variables and track them.

        Args:
            variables: Dictionary of variables to load

        Returns:
            Number of variables actually loaded (new ones)
        """
        loaded_count = 0

        for key, value in variables.items():
            # Store original value if not already tracked
            if key not in self.loaded_vars:
                self.loaded_vars.add(key)
                loaded_count += 1

            # Set the environment variable
            os.environ[key] = value

        # Save state
        self._save_state()

        return loaded_count

    def unload_all(self) -> int:
        """Unload all tracked variables.

        Returns:
            Number of variables unloaded
        """
        unloaded_count = 0

        for key in list(self.loaded_vars):
            if key in os.environ:
                del os.environ[key]
                unloaded_count += 1

        # Clear tracking
        self.loaded_vars.clear()
        self.original_values.clear()

        # Clear state file
        if self.state_file.exists():
            self.state_file.unlink()

        return unloaded_count

    def _save_state(self) -> None:
        """Save tracking state to file.

        Creates the directory if needed and sets restrictive permissions.
        """
        # Create directory if it doesn't exist
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        state = {
            'loaded_vars': list(self.loaded_vars),
            'original_values': self.original_values,
        }

        # Write state file
        with open(self.state_file, 'w') as f:
            json.dump(state, f)

        # Set restrictive permissions (owner read/write only)
        os.chmod(self.state_file, stat.S_IRUSR | stat.S_IWUSR)

    def load_state(self) -> bool:
        """Load tracking state from file.

        Returns:
            True if state was loaded, False if no state file exists
        """
        if not self.state_file.exists():
            return False

        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)

            self.loaded_vars = set(state.get('loaded_vars', []))
            self.original_values = state.get('original_values', {})

            return True
        except (json.JSONDecodeError, KeyError, IOError):
            # If state file is corrupted, ignore it
            return False

    def get_loaded_variables(self) -> Dict[str, str]:
        """Get currently loaded variables.

        Returns:
            Dictionary of currently loaded variables
        """
        result = {}
        for key in self.loaded_vars:
            if key in os.environ:
                result[key] = os.environ[key]
        return result

    def is_tracked(self, key: str) -> bool:
        """Check if a variable is tracked.

        Args:
            key: Environment variable name

        Returns:
            True if the variable is tracked
        """
        return key in self.loaded_vars

    def get_status(self) -> Tuple[int, Set[str]]:
        """Get tracking status.

        Returns:
            Tuple of (count of loaded variables, set of variable names)
        """
        return len(self.loaded_vars), self.loaded_vars.copy()
