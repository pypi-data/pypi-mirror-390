# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Shell auto-completion support
- Environment diffing command
- Template generation (.env.example)
- YAML/JSON export functionality
- Multiple file loading support

## [0.0.1] - 2025-11-10

### Added

#### Core Functionality
- Full support for all assignment operators:
  - `=` - Standard assignment
  - `:=` - Immediate expansion (Makefile-style)
  - `+=` - Append to existing variable
  - `?=` - Conditional assignment (only if unset)

- Comprehensive variable expansion:
  - `${VAR}` - Basic expansion from environment
  - `${VAR:-default}` - Use default if unset (no assignment)
  - `${VAR:=default}` - Assign default if unset, then use it
  - `${VAR:+alt}` - Use alternate value if set

- Environment variable tracking:
  - Track loaded variables for proper unloading
  - Persist state across CLI invocations
  - Safe unloading of only loaded variables

- File parsing:
  - Comment support (`#` and inline)
  - Quoted value support (single and double quotes)
  - Escape sequence processing in double quotes
  - Multiline value support
  - Export prefix support (`export KEY=value`)
  - Empty value handling

#### CLI Commands
- `load-dotenv` command:
  - Auto-discover .env files from current directory or parents
  - Load from specific file path
  - `--override` flag to force override existing variables
  - `--verbose` flag for detailed output
  - `--state-file` option to customize state file location

- `unload-dotenv` command:
  - Remove all tracked environment variables
  - `--verbose` flag for detailed output
  - `--force` flag to skip confirmation prompt
  - `--state-file` option to customize state file location

- `set-dotenv` command:
  - Set individual variables: `set-dotenv KEY VALUE` or `set-dotenv KEY=VALUE`
  - Remove variables: `set-dotenv --remove KEY`
  - List all variables: `set-dotenv --list`
  - Edit .env file: `set-dotenv --edit`
  - `--operator` flag to choose assignment operator (=, :=, +=, ?=)
  - `--file` option to work with custom .env files
  - `--editor` option to specify custom editor
  - Auto-creates .env file if it doesn't exist
  - Infers operator from `KEY=VALUE` format

#### Testing
- Comprehensive test suite with 100% coverage:
  - Parser tests (test_parser.py)
  - Expansion tests (test_expansion.py)
  - Tracker tests (test_tracker.py)
  - Core tests (test_core.py)
  - CLI tests (test_cli.py)

#### Documentation
- README.md with:
  - Project overview
  - Quick start guide
  - Feature highlights
  - Installation instructions
  - Basic usage examples

- USAGE.md with:
  - Complete command reference
  - Detailed syntax documentation
  - Assignment operator explanations
  - Variable expansion guide
  - Real-world examples
  - Integration guides (Shell, Python, Makefile, Docker)
  - Troubleshooting section
  - FAQ

#### Packaging
- Modern packaging with pyproject.toml
- Entry points for CLI commands (load-dotenv, unload-dotenv, set-dotenv)
- Package renamed from `load-dotenv` to `dotenv-tools`
- Comprehensive metadata
- Development dependencies configuration
- Python 3.8+ support
- MIT License

#### Build System
- Hatchling build backend
- Source and wheel distribution support
- Twine upload configuration
- GitHub repository ready

### Technical Details
- **Parser:** Custom regex-based parser supporting all operators
- **Expansion Engine:** Recursive variable substitution with circular reference detection
- **Tracker:** JSON-based state persistence with restrictive file permissions
- **SetDotenv:** Class for setting, updating, and removing variables in .env files
- **CLI Framework:** Click for professional command-line interface
- **Dependencies:** Only Click (click>=8.0.0)
- **Python Compatibility:** 3.8, 3.9, 3.10, 3.11, 3.12

### Author
- LousyBook01 (GitHub: @LousyBook94)

---

## Version History

- **0.0.1** - Initial release with full feature set (load, unload, set, edit, list, remove)

---

## Support

For issues or questions, visit:
- GitHub: https://github.com/LousyBook94/load-dotenv
- Issues: https://github.com/LousyBook94/load-dotenv/issues
