"""Tests for the expansion module."""

import pytest
from src.dotenv_tools.expansion import (
    expand_variables,
    expand_immediate,
    ExpansionError,
)


class TestExpandVariables:
    """Test variable expansion."""

    def test_no_expansion(self):
        """Test value without variables."""
        result = expand_variables("simple value", {})
        assert result == "simple value"

    def test_simple_expansion(self):
        """Test simple ${VAR} expansion."""
        env = {"VAR": "value"}
        result = expand_variables("${VAR}", env)
        assert result == "value"

    def test_multiple_expansions(self):
        """Test multiple variables in one value."""
        env = {"VAR1": "hello", "VAR2": "world"}
        result = expand_variables("${VAR1} ${VAR2}", env)
        assert result == "hello world"

    def test_expansion_with_text(self):
        """Test expansion mixed with text."""
        env = {"VAR": "test"}
        result = expand_variables("prefix-${VAR}-suffix", env)
        assert result == "prefix-test-suffix"

    def test_undefined_variable(self):
        """Test undefined variable."""
        result = expand_variables("${UNDEFINED}", {})
        assert result == "${UNDEFINED}"

    def test_default_minus(self):
        """Test ${VAR:-default} syntax."""
        env = {}
        result = expand_variables("${VAR:-default}", env)
        assert result == "default"

    def test_default_minus_with_value(self):
        """Test ${VAR:-default} when VAR is set."""
        env = {"VAR": "value"}
        result = expand_variables("${VAR:-default}", env)
        assert result == "value"

    def test_default_equals(self):
        """Test ${VAR:=default} syntax."""
        env = {}
        result = expand_variables("${VAR:=default}", env)
        assert result == "default"

        # Should assign the default
        assert env["VAR"] == "default"

    def test_default_equals_with_value(self):
        """Test ${VAR:=default} when VAR is set."""
        env = {"VAR": "value"}
        result = expand_variables("${VAR:=default}", env)
        assert result == "value"

        # Should not modify existing value
        assert env["VAR"] == "value"

    def test_alternate_plus(self):
        """Test ${VAR:+alt} syntax."""
        env = {"VAR": "value"}
        result = expand_variables("${VAR:+alternate}", env)
        assert result == "alternate"

    def test_alternate_plus_unset(self):
        """Test ${VAR:+alt} when VAR is unset."""
        env = {}
        result = expand_variables("${VAR:+alternate}", env)
        assert result == ""

    def test_nested_expansion(self):
        """Test nested variable references."""
        env = {"VAR1": "hello", "VAR2": "${VAR1} world"}
        result = expand_variables("${VAR2}", env)
        assert result == "hello world"

    def test_circular_reference(self):
        """Test circular reference detection."""
        env = {"A": "${B}", "B": "${A}"}
        with pytest.raises(ExpansionError):
            expand_variables("${A}", env)


class TestExpandImmediate:
    """Test immediate expansion (for := operator)."""

    def test_immediate_expansion(self):
        """Test immediate expansion works."""
        env = {"VAR": "value"}
        result = expand_immediate("${VAR}", env)
        assert result == "value"

    def test_immediate_expansion_order(self):
        """Test that immediate expansion happens at assignment time."""
        env = {}
        # This should not expand because env is empty
        result = expand_immediate("${VAR}", env)
        assert result == "${VAR}"
