"""Dotenv-tools: A comprehensive CLI tool to manage environment variables in .env files.

This package provides:
- load-dotenv command to load .env files
- unload-dotenv command to remove loaded variables
- set-dotenv command to set, update, or remove environment variables
- Support for all dotenv syntax: =, :=, +=, ?=
- Variable expansion: ${VAR}, ${VAR:-default}, ${VAR:=default}, ${VAR:+alt}
- Export prefix support
"""

__version__ = "0.0.1"
__author__ = "LousyBook01"
__email__ = "lousybook94@gmail.com"
__description__ = "A comprehensive CLI tool to manage environment variables in .env files"

# Expose main classes
from .core import LoadDotenv
from .tracker import Tracker
from .setter import SetDotenv

__all__ = [
    "LoadDotenv",
    "Tracker",
    "SetDotenv",
]
