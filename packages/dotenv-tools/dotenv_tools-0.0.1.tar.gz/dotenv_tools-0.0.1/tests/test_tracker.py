"""Tests for the tracker module."""

import os
import tempfile
from pathlib import Path
from src.dotenv_tools.tracker import Tracker


class TestTracker:
    """Test environment variable tracking."""

    def test_snapshot_environment(self):
        """Test snapshotting current environment."""
        tracker = Tracker(Path(tempfile.mktemp()))

        # Set a test variable
        os.environ['TEST_VAR'] = 'test_value'

        tracker.snapshot_environment()

        # Check that the variable is in original_values
        assert 'TEST_VAR' in tracker.original_values
        assert tracker.original_values['TEST_VAR'] == 'test_value'

    def test_load_variables(self):
        """Test loading and tracking variables."""
        tracker = Tracker(Path(tempfile.mktemp()))

        variables = {
            'VAR1': 'value1',
            'VAR2': 'value2',
        }

        loaded_count = tracker.load_variables(variables)

        assert loaded_count == 2
        assert tracker.is_tracked('VAR1')
        assert tracker.is_tracked('VAR2')
        assert os.environ['VAR1'] == 'value1'
        assert os.environ['VAR2'] == 'value2'

    def test_unload_all(self):
        """Test unloading all tracked variables."""
        tracker = Tracker(Path(tempfile.mktemp()))

        # Load some variables
        variables = {'VAR1': 'value1', 'VAR2': 'value2'}
        tracker.load_variables(variables)

        # Unload
        unloaded = tracker.unload_all()

        assert unloaded == 2
        assert 'VAR1' not in os.environ
        assert 'VAR2' not in os.environ
        assert len(tracker.loaded_vars) == 0

    def test_get_loaded_variables(self):
        """Test getting currently loaded variables."""
        tracker = Tracker(Path(tempfile.mktemp()))

        variables = {'VAR1': 'value1', 'VAR2': 'value2'}
        tracker.load_variables(variables)

        loaded = tracker.get_loaded_variables()

        assert loaded == variables

    def test_is_tracked(self):
        """Test checking if a variable is tracked."""
        tracker = Tracker(Path(tempfile.mktemp()))

        variables = {'VAR1': 'value1'}
        tracker.load_variables(variables)

        assert tracker.is_tracked('VAR1')
        assert not tracker.is_tracked('UNTRACKED')

    def test_get_status(self):
        """Test getting tracker status."""
        tracker = Tracker(Path(tempfile.mktemp()))

        variables = {'VAR1': 'value1', 'VAR2': 'value2', 'VAR3': 'value3'}
        tracker.load_variables(variables)

        count, loaded = tracker.get_status()

        assert count == 3
        assert loaded == {'VAR1', 'VAR2', 'VAR3'}
