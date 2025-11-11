"""Variable expansion engine for dotenv values.

Supports:
- ${VAR} - Basic expansion from environment
- ${VAR:-default} - Use default if unset (no assignment)
- ${VAR:=default} - Assign default if unset, then use it
- ${VAR:+alt} - Use alternate if set
"""

import os
import re
from typing import Dict, Optional, Tuple


class ExpansionError(Exception):
    """Raised when variable expansion fails."""
    pass


def expand_variables(value: str, env: Dict[str, str], max_iterations: int = 100) -> str:
    """Expand all variables in a value string with nested expansion support.

    Args:
        value: The value string containing variable references
        env: Environment variables dictionary
        max_iterations: Maximum expansion iterations to prevent infinite loops

    Returns:
        Expanded value string

    Raises:
        ExpansionError: If circular reference or other expansion error
    """
    if not value or '${' not in value:
        return value

    # Track variables being expanded to detect circular references
    expanding = set()

    def replace_var(match: re.Match) -> str:
        expression = match.group(1).strip()

        # Check for circular reference
        if expression in expanding:
            raise ExpansionError(f"Circular variable reference detected: {expression}")

        expanding.add(expression)
        try:
            result = _expand_expression(expression, env)
            expanding.remove(expression)
            return result
        except Exception as e:
            expanding.remove(expression)
            raise e

    # Iterative expansion to handle nested references
    result = value
    last_result = None
    iterations = 0

    while result != last_result and iterations < max_iterations:
        if '${' not in result:
            break

        last_result = result
        try:
            # Pattern to match ${...} expressions
            pattern = r'\$\{([^}]+)\}'
            result = re.sub(pattern, replace_var, result)
            iterations += 1
        except RecursionError:
            raise ExpansionError("Circular variable reference detected")

    if iterations >= max_iterations:
        raise ExpansionError("Maximum expansion iterations reached (possible circular reference)")

    return result


def _expand_expression(expression: str, env: Dict[str, str]) -> str:
    """Expand a single ${...} expression.

    Args:
        expression: The content inside ${...}
        env: Environment variables dictionary

    Returns:
        Expanded result

    Examples:
        - "VAR" -> value of VAR from env
        - "VAR:-default" -> VAR or "default" if unset
        - "VAR:=default" -> set VAR to "default" if unset, then use it
        - "VAR:+alt" -> "alt" if VAR is set, else empty string
    """
    # Check for operators in order of precedence
    # Match :-, :=, or :+ (colon-based operators)
    colon_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*):(\+|-|=)(.*)$', expression)

    if colon_match:
        var_name = colon_match.group(1)
        operator = colon_match.group(2)
        value = colon_match.group(3)

        var_exists = var_name in env and env[var_name] is not None

        if operator == '+':
            # ${VAR:+alt} - use alternate if set
            return value if var_exists else ""
        elif operator == '-':
            # ${VAR:-default} - just use default, don't assign
            return env.get(var_name, value)
        elif operator == '=':
            # ${VAR:=default} - assign default if unset, then use it
            if not var_exists:
                env[var_name] = value
            return env.get(var_name, value)

    # Simple ${VAR} - just expand from environment
    var_name = expression
    return env.get(var_name, f"${{{var_name}}}")


def expand_immediate(value: str, env: Dict[str, str]) -> str:
    """Expand variables immediately (for := operator).

    This expands variables in the value at assignment time,
    using only the current environment state.

    Args:
        value: The value string
        env: Current environment variables

    Returns:
        Expanded value
    """
    return expand_variables(value, env)
