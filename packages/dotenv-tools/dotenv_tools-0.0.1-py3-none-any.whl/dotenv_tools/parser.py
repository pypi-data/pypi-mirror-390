"""Custom dotenv parser with support for all assignment operators.

Supports:
- KEY=value - Standard assignment
- KEY:=value - Immediate expansion
- KEY+=value - Append to existing
- KEY?=value - Conditional assignment (only if unset)
- export KEY=value - Export prefix
"""

import re
from typing import List, Optional, Tuple, Dict


class ParseError(Exception):
    """Raised when a .env line cannot be parsed."""
    pass


# Regex patterns for different operators
PATTERNS = {
    '?=': re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\?\=(.*)$'),
    '+=': re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\+\=(.*)$'),
    ':=': re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\:\=(.*)$'),
    '=': re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\=(.*)$'),
}


def parse_line(line: str) -> Optional[Tuple[str, str, str]]:
    """Parse a single line from a .env file.

    Args:
        line: A line from the .env file

    Returns:
        Tuple of (key, operator, value) or None if line should be ignored

    Raises:
        ParseError: If line has invalid syntax
    """
    # Strip leading/trailing whitespace
    line = line.strip()

    # Skip empty lines
    if not line:
        return None

    # Skip comment lines (start with #)
    if line.startswith('#'):
        return None

    # Check for export prefix
    export_prefix = False
    if line.startswith('export '):
        export_prefix = True
        line = line[7:].strip()  # Remove 'export ' prefix

    # Try to match each operator pattern
    for op, pattern in PATTERNS.items():
        match = pattern.match(line)
        if match:
            key = match.group(1)
            value = match.group(2).strip() if match.group(2) else ''

            # Handle inline comments (but not in quoted strings)
            value = _strip_inline_comment(value)

            # Parse quoted strings
            value = _parse_quoted_value(value)

            if export_prefix:
                key = f"export {key}"

            return key, op, value

    # If we get here, the line doesn't match any pattern
    raise ParseError(f"Invalid syntax: {line}")


def _strip_inline_comment(value: str) -> str:
    """Remove inline comments from a value.

    Comments start with # and are only recognized outside quotes.
    """
    in_single_quote = False
    in_double_quote = False
    escaped = False

    for i, char in enumerate(value):
        if escaped:
            escaped = False
            continue

        if char == '\\':
            escaped = True
            continue

        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            continue

        if char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            continue

        if char == '#' and not in_single_quote and not in_double_quote:
            return value[:i].rstrip()

    return value


def _parse_quoted_value(value: str) -> str:
    """Parse quoted values, handling escapes and multiline.

    Args:
        value: The value string which may be quoted

    Returns:
        Unquoted and processed value
    """
    value = value.strip()

    # If not quoted, return as-is
    if not ((value.startswith('"') and value.endswith('"')) or
            (value.startswith("'") and value.endswith("'"))):
        return value

    # Remove outer quotes
    quote_char = value[0]
    value = value[1:-1]

    if quote_char == '"':
        # Double quotes - handle escapes
        value = _process_double_quotes(value)
    else:
        # Single quotes - no escape processing
        pass

    return value


def _process_double_quotes(value: str) -> str:
    r"""Process double-quoted strings with escape sequences.

    Supported escapes:
        \" - Double quote
        \\n - Newline
        \\t - Tab
        \\r - Carriage return
        \\\ - Backslash
    """
    result = []
    escaped = False

    for char in value:
        if escaped:
            escape_map = {
                'n': '\n',
                't': '\t',
                'r': '\r',
                '"': '"',
                '\\': '\\',
            }
            result.append(escape_map.get(char, char))
            escaped = False
        elif char == '\\':
            escaped = True
        else:
            result.append(char)

    return ''.join(result)


def parse_file(content: str) -> List[Tuple[str, str, str]]:
    """Parse a complete .env file.

    Args:
        content: The content of the .env file

    Returns:
        List of (key, operator, value) tuples

    Raises:
        ParseError: If any line has invalid syntax
    """
    lines = content.split('\n')
    results = []

    for line_num, line in enumerate(lines, 1):
        try:
            parsed = parse_line(line)
            if parsed:
                results.append(parsed)
        except ParseError as e:
            raise ParseError(f"Line {line_num}: {e}")

    return results


def parse_file_to_dict(content: str) -> Dict[str, Tuple[str, str]]:
    """Parse a .env file to a dictionary.

    Args:
        content: The content of the .env file

    Returns:
        Dictionary mapping key to (operator, value)

    Raises:
        ParseError: If any line has invalid syntax
    """
    parsed_lines = parse_file(content)
    result = {}

    for key, op, value in parsed_lines:
        # Handle export prefix
        if key.startswith('export '):
            key = key[7:]

        result[key] = (op, value)

    return result
