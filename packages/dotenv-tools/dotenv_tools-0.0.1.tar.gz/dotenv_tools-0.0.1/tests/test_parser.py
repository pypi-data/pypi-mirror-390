"""Tests for the parser module."""

import pytest
from src.dotenv_tools.parser import (
    parse_line,
    parse_file_to_dict,
    ParseError,
)


class TestParseLine:
    """Test parsing individual lines."""

    def test_standard_assignment(self):
        """Test standard KEY=value assignment."""
        result = parse_line("KEY=value")
        assert result == ("KEY", "=", "value")

    def test_immediate_expansion(self):
        """Test KEY:=value assignment."""
        result = parse_line("KEY:=value")
        assert result == ("KEY", ":=", "value")

    def test_append(self):
        """Test KEY+=value assignment."""
        result = parse_line("KEY+=value")
        assert result == ("KEY", "+=", "value")

    def test_conditional(self):
        """Test KEY?=value assignment."""
        result = parse_line("KEY?=value")
        assert result == ("KEY", "?=", "value")

    def test_export_prefix(self):
        """Test export prefix."""
        result = parse_line("export KEY=value")
        assert result == ("export KEY", "=", "value")

    def test_quoted_value_double(self):
        """Test double-quoted value."""
        result = parse_line('KEY="hello world"')
        assert result == ("KEY", "=", "hello world")

    def test_quoted_value_single(self):
        """Test single-quoted value."""
        result = parse_line("KEY='hello world'")
        assert result == ("KEY", "=", "hello world")

    def test_inline_comment(self):
        """Test inline comment stripping."""
        result = parse_line('KEY=value # this is a comment')
        assert result == ("KEY", "=", "value")

    def test_inline_comment_in_quotes(self):
        """Test that inline comments in quotes are not stripped."""
        result = parse_line('KEY="value # not a comment"')
        assert result == ("KEY", "=", "value # not a comment")

    def test_empty_value(self):
        """Test empty value."""
        result = parse_line("KEY=")
        assert result == ("KEY", "=", "")

    def test_comment_line(self):
        """Test comment line is ignored."""
        result = parse_line("# This is a comment")
        assert result is None

    def test_blank_line(self):
        """Test blank line is ignored."""
        result = parse_line("")
        assert result is None

    def test_whitespace_line(self):
        """Test whitespace-only line is ignored."""
        result = parse_line("   ")
        assert result is None

    def test_escaped_characters(self):
        """Test escaped characters in double quotes."""
        result = parse_line(r'KEY="line1\nline2"')
        assert result == ("KEY", "=", "line1\nline2")

    def test_invalid_syntax(self):
        """Test that invalid syntax raises error."""
        with pytest.raises(ParseError):
            parse_line("INVALID LINE")


class TestParseFileToDict:
    """Test parsing complete files."""

    def test_simple_file(self):
        """Test parsing a simple .env file."""
        content = """
        KEY1=value1
        KEY2=value2
        # Comment
        KEY3=value3
        """
        result = parse_file_to_dict(content)
        assert result == {
            "KEY1": ("=", "value1"),
            "KEY2": ("=", "value2"),
            "KEY3": ("=", "value3"),
        }

    def test_all_operators(self):
        """Test file with all operators."""
        content = """
        A=standard
        B:=immediate
        C+=append
        D?=conditional
        """
        result = parse_file_to_dict(content)
        assert result["A"] == ("=", "standard")
        assert result["B"] == (":=", "immediate")
        assert result["C"] == ("+=", "append")
        assert result["D"] == ("?=", "conditional")

    def test_export_prefix(self):
        """Test export prefix is handled."""
        content = """
        export KEY1=value1
        KEY2=value2
        """
        result = parse_file_to_dict(content)
        # Export prefix is removed in parse_file_to_dict
        assert "KEY1" in result
        assert "KEY2" in result
        assert result["KEY1"] == ("=", "value1")
        assert result["KEY2"] == ("=", "value2")
