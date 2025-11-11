# Dotenv-Tools Usage Guide

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Commands](#commands)
  - [load-dotenv](#load-dotenv)
  - [unload-dotenv](#unload-dotenv)
  - [set-dotenv](#set-dotenv)
- [Assignment Operators](#assignment-operators)
- [Variable Expansion](#variable-expansion)
- [Syntax Reference](#syntax-reference)
- [Examples](#examples)
- [Integration](#integration)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## Installation

### From PyPI

```bash
pip install dotenv-tools
```

### From Source

```bash
git clone https://github.com/LousyBook94/load-dotenv.git
cd load-dotenv
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/LousyBook94/load-dotenv.git
cd load-dotenv

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Package Information

- **Package Name**: dotenv-tools
- **Repository Name**: load-dotenv
- **Author**: LousyBook01
- **Version**: 0.0.1

---

## Quick Start

**Method 1: Create .env file manually and load it**

1. Create a `.env` file in your project:

```bash
DATABASE_URL=postgres://localhost/mydb
API_KEY=your-api-key
DEBUG=true
```

2. Load the environment variables:

```bash
load-dotenv
```

3. Use the variables in your application:

```bash
echo $DATABASE_URL  # postgres://localhost/mydb
```

4. When done, unload the variables:

```bash
unload-dotenv
```

**Method 2: Use set-dotenv to manage .env file**

1. Set variables directly:

```bash
set-dotenv DATABASE_URL postgres://localhost/mydb
set-dotenv API_KEY=your-api-key
set-dotenv DEBUG=true
```

2. List variables in .env:

```bash
set-dotenv --list
```

3. Load and use:

```bash
load-dotenv
echo $DATABASE_URL  # postgres://localhost/mydb
```

4. Clean up when done:

```bash
unload-dotenv
```

---

## Commands

Dotenv-tools provides three main commands:

- **load-dotenv**: Load environment variables from a .env file
- **unload-dotenv**: Remove all loaded environment variables
- **set-dotenv**: Set, update, or remove variables in .env files

### load-dotenv

Load environment variables from a `.env` file.

**Usage:**

```bash
load-dotenv [FILE] [OPTIONS]
```

**Arguments:**

- `FILE` - Path to `.env` file (optional, auto-discovers if not provided)

**Options:**

- `-o, --override` - Override existing environment variables
- `--state-file PATH` - Path to state file (default: `~/.load_dotenv_state.json`)
- `-v, --verbose` - Show detailed output
- `-h, --help` - Show help message

**Examples:**

```bash
# Load from .env in current directory
load-dotenv

# Load from specific file
load-dotenv /path/to/production.env

# Load with verbose output
load-dotenv --verbose

# Force override existing variables
load-dotenv --override

# Load and show all loaded variables
load-dotenv --verbose
```

---

### unload-dotenv

Remove all environment variables loaded by this tool.

**Usage:**

```bash
unload-dotenv [OPTIONS]
```

**Options:**

- `--state-file PATH` - Path to state file (default: `~/.load_dotenv_state.json`)
- `-v, --verbose` - Show detailed output
- `-f, --force` - Unload without confirmation
- `-h, --help` - Show help message

**Examples:**

```bash
# Unload all variables
unload-dotenv

# Unload with verbose output
unload-dotenv --verbose

# Force unload without confirmation
unload-dotenv --force
```

---

### set-dotenv

Set, update, or remove environment variables in `.env` files.

**Usage:**

```bash
set-dotenv [KEY_VALUE]... [OPTIONS]
```

**Arguments:**

- `KEY_VALUE` - Variable name and value (format: `KEY VALUE` or `KEY=VALUE`)

**Options:**

- `-f, --file PATH` - Path to `.env` file (default: finds or creates .env in current directory)
- `-r, --remove` - Remove the specified variable
- `-o, --operator` - Assignment operator (`=`, `:=`, `+=`, `?=`) (default: `=`)
- `-e, --edit` - Edit the `.env` file with your default editor
- `--editor TEXT` - Editor to use for editing (default: `$EDITOR` or `$VISUAL`)
- `-l, --list` - List all variables in the `.env` file
- `-v, --verbose` - Show detailed output
- `-h, --help` - Show help message

**Examples:**

```bash
# Set a variable with space-separated format
set-dotenv PORT 3000

# Set a variable with = format
set-dotenv API_KEY=secret123

# Set with specific operator
set-dotenv --operator := FULL_PATH ${HOME}/myapp

# Remove a variable
set-dotenv --remove API_KEY

# List all variables
set-dotenv --list

# Edit .env file
set-dotenv --edit

# Use custom .env file
set-dotenv --file .env.production PORT 8080

# Edit with specific editor
set-dotenv --edit --editor vim
```

**Supported Formats:**

1. **Space-separated**: `set-dotenv KEY VALUE`
2. **Equals format**: `set-dotenv KEY=VALUE`
3. **With operator**: `set-dotenv KEY:=VALUE`, `set-dotenv KEY+=VALUE`, `set-dotenv KEY?=VALUE`

**Common Use Cases:**

```bash
# Add a new variable
set-dotenv DATABASE_URL postgres://localhost/mydb

# Update existing variable
set-dotenv PORT 3000

# Append to PATH
set-dotenv --operator += PATH /opt/myapp/bin

# Set conditional default
set-dotenv --operator ?= API_KEY ${DEFAULT_API_KEY}

# List and review before loading
set-dotenv --list
load-dotenv
```

---

## Assignment Operators

Dotenv-tools supports multiple assignment operators for different behaviors:

### `=` - Standard Assignment

Sets the variable to the value (deferred expansion).

```bash
PORT=3000
HOST=localhost
```

**Behavior:**
- Expands variables after all variables are parsed
- Respects `--override` flag

### `:=` - Immediate Expansion

Expands variables immediately at assignment time (Makefile-style).

```bash
PATH:=$PATH:/new/directory
BASE_DIR:=${HOME}/myapp
```

**Behavior:**
- Variables are expanded right when the line is processed
- Uses the environment state at assignment time
- Can reference variables defined earlier in the file

### `+=` - Append

Appends to an existing variable.

```bash
PATH+=/opt/myapp/bin
LIBS+=-lm
```

**Behavior:**
- Appends the value to the current value (no separator)
- Creates the variable if it doesn't exist
- Useful for PATH-like variables

### `?=` - Conditional Assignment

Only sets the variable if it's not already set.

```bash
API_KEY?=${DEFAULT_KEY}
PORT?=8080
```

**Behavior:**
- Checks if variable is unset in the environment
- If unset, assigns the value
- If set, keeps the existing value

---

## Variable Expansion

Dotenv-tools supports comprehensive variable expansion:

### `${VAR}` - Basic Expansion

Expands the variable from the environment.

```bash
USER=john
GREETING=Hello ${USER}
# Result: GREETING=Hello john
```

### `${VAR:-default}` - Default Value (No Assignment)

Uses a default value if the variable is unset. Does not modify the environment.

```bash
PORT=${PORT:-8080}
HOST=${HOST:-localhost}
```

**Example:**
- If `PORT` is unset: Uses `8080` in this context only
- If `PORT` is set to `3000`: Uses `3000`

### `${VAR:=default}` - Default Value with Assignment

Assigns a default value if the variable is unset, then uses it.

```bash
DB_NAME:=${DEFAULT_DB_NAME:-mydb}
```

**Example:**
- If `DEFAULT_DB_NAME` is unset: Sets `DB_NAME=mydb` in the environment
- If `DEFAULT_DB_NAME` is set to `testdb`: Sets `DB_NAME=testdb` in the environment

### `${VAR:+alternate}` - Alternate Value

Uses an alternate value if the variable IS set. Returns empty string if unset.

```bash
DEBUG_MODE=${DEBUG:+--debug}
```

**Example:**
- If `DEBUG` is set: `DEBUG_MODE=--debug`
- If `DEBUG` is unset: `DEBUG_MODE=` (empty)

---

## Syntax Reference

### Comments

```bash
# This is a full-line comment
KEY=value # This is an inline comment
```

**Rules:**
- `#` starts a comment (outside of quotes)
- Comments can be on their own line or inline
- Comments inside quoted strings are NOT processed as comments

### Quoted Values

**Double Quotes:**

```bash
MESSAGE="Hello World"
MULTILINE="Line 1\nLine 2"
```

**Supported escapes in double quotes:**
- `\"` - Double quote
- `\\` - Backslash
- `\n` - Newline
- `\t` - Tab
- `\r` - Carriage return

**Single Quotes:**

```bash
MESSAGE='Hello World'
LITERAL='No ${EXPANSION}'
```

**Notes:**
- Single quotes preserve literal values (no escape processing)
- No variable expansion inside single quotes

### Empty Values

```bash
EMPTY=
ALSO_EMPTY=""
```

Both result in empty string values.

### Export Prefix

```bash
export API_KEY=secret
export DB_HOST=localhost
```

**Notes:**
- `export` prefix is supported
- The export prefix is removed from the variable name
- Makes variables available to child processes (like standard shell)

### Special Characters

```bash
# Spaces around = are not allowed in keys
PORT=3000  # Valid
PORT =3000 # Invalid

# Keys can contain letters, numbers, and underscores
VALID_KEY_123=value
_UNDERSCORE=value
```

---

## Examples

### Example 1: Basic Configuration

```bash
# .env file
APP_NAME=MyAwesomeApp
APP_ENV=development
DEBUG=true
PORT=3000
HOST=localhost
```

```bash
$ load-dotenv --verbose
Loading environment variables from .env...
  APP_NAME = MyAwesomeApp
  APP_ENV = development
  DEBUG = true
  PORT = 3000
  HOST = localhost

✓ Successfully loaded 5 environment variables
```

### Example 2: Database Configuration

```bash
# .env file with variable expansion
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=admin
DB_PASS=secret

# Expand other variables
DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}
```

**Result:**
```
DATABASE_URL=postgresql://admin:secret@localhost:5432/myapp
```

### Example 3: Environment-Specific Settings

```bash
# .env file
ENV=development
DEBUG?=true
API_URL=${API_URL_BASE}/v1
```

```bash
# Terminal 1 - development
$ export API_URL_BASE=https://dev.example.com
$ load-dotenv
# DEBUG=true (from ?= because not set)
# API_URL=https://dev.example.com/v1

# Terminal 2 - production
$ export DEBUG=false
$ export API_URL_BASE=https://api.example.com
$ load-dotenv
# DEBUG=false (kept because already set, ?= didn't override)
# API_URL=https://api.example.com/v1
```

### Example 4: PATH Management

```bash
# .env file
PATH+=/opt/myapp/bin
PATH+=/opt/myapp/sbin
```

```bash
$ load-dotenv
$ echo $PATH
/usr/local/bin:/usr/bin:/opt/myapp/bin:/opt/myapp/sbin
```

### Example 5: Conditional Defaults

```bash
# .env file
DEFAULT_PORT=8080
CUSTOM_PORT?=${DEFAULT_PORT}
```

If `CUSTOM_PORT` is not set in the environment, it will be set to the value of `DEFAULT_PORT` (or `8080` if that's also unset).

### Example 6: Debug Mode Toggle

```bash
# .env file
DEBUG=true
VERBOSE=${DEBUG:+--verbose}
```

**Result:**
```
VERBOSE=--verbose
```

If `DEBUG` was unset, `VERBOSE` would be empty.

---

## Integration

### Shell Integration (Bash/Zsh)

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Dotenv-tools shortcuts
alias loadenv='load-dotenv'
alias unloadenv='unload-dotenv'
alias setenv='set-dotenv'

# Or full functions
load-dotenv() {
    python -m dotenv_tools.cli load-dotenv "$@"
}

unload-dotenv() {
    python -m dotenv_tools.cli unload-dotenv "$@"
}

set-dotenv() {
    python -m dotenv_tools.cli set-dotenv "$@"
}
```

Usage:

```bash
load-dotenv
echo $DATABASE_URL
unload-dotenv
```

### Python Script

```python
import subprocess
import os

# Load .env
subprocess.run(['load-dotenv'], check=True)

# Use environment variables
print(os.environ['DATABASE_URL'])

# Unload
subprocess.run(['unload-dotenv', '--force'], check=True)
```

### Makefile

```makefile
.PHONY: env-load env-unload test

env-load:
	load-dotenv

env-unload:
	unload-dotenv --force

test: env-load
	pytest
	env-unload
```

Usage:

```bash
make test
```

### Docker

```dockerfile
FROM python:3.11-slim

# Install dotenv-tools
RUN pip install dotenv-tools

# Copy .env file
COPY .env .

# Load .env and run app
CMD ["sh", "-c", "load-dotenv && python app.py"]
```

---

## Troubleshooting

### File Not Found

**Error:** `File not found: /path/to/.env`

**Solution:**
- Check that the file exists: `ls -la /path/to/.env`
- Provide the full path: `load-dotenv /full/path/to/.env`
- Ensure you're in the right directory

### No .env File Found

**Error:** `No .env file found starting from /current/path`

**Solution:**
- Create a `.env` file in your project root
- Or provide a specific file path: `load-dotenv /path/to/custom.env`

### Variables Not Loading

**Possible causes:**
1. File has syntax errors
2. Variables are already set and `--override` is not used
3. File encoding issue (should be UTF-8)

**Solutions:**
- Use `--verbose` to see what's happening
- Check file syntax in the examples
- Use `--override` to force load
- Ensure file is UTF-8 encoded

### Unload Not Working

**Error:** `No environment variables to unload`

**Solution:**
- Check if state file exists: `ls -la ~/.load_dotenv_state.json`
- Variables might have been cleared by another process
- State file might be corrupted (delete and retry)

### Circular Reference

**Error:** `Circular variable reference detected`

**Solution:**
- Check your .env file for variables that reference each other
- Example: `A=${B}` and `B=${A}` is a circular reference

### Permission Denied

**Error:** `PermissionError` when creating state file

**Solution:**
- Ensure you have write access to your home directory
- Check home directory permissions: `ls -ld ~`

---

## FAQ

**Q: Can I load multiple .env files?**

A: Yes! You can chain commands or use set-dotenv:

**Method 1: Chain load-dotenv commands**
```bash
load-dotenv .env.base && load-dotenv .env.local
```

**Method 2: Use set-dotenv to manage multiple files**
```bash
set-dotenv --file .env.development DEBUG=true
set-dotenv --file .env.production DEBUG=false
```

**Q: Do I need to unload variables?**

A: The variables are only loaded into your current shell session. They will be cleared when the shell exits. Use `unload-dotenv` to manually clear them.

**Q: Are loaded variables persistent?**

A: No, variables are only loaded for the current session. State is tracked in `~/.load_dotenv_state.json` for unload purposes, but doesn't persist the variables themselves.

**Q: Can I load .env in a Python script programmatically?**

A: Yes! You can use the Python API:
```python
from dotenv_tools import LoadDotenv, Tracker

loader = LoadDotenv('.env')
variables = loader.load()
tracker = Tracker('~/.load_dotenv_state.json')
tracker.load_variables(variables)
```

**Q: What happens if I don't use `--override`?**

A: Variables that already exist in your environment will be skipped. Use `--override` to force load all variables.

**Q: Are quotes required?**

A: Only if your value contains spaces or special characters. For example:
- `KEY=value` - No quotes needed
- `KEY="value with spaces"` - Quotes required

**Q: Does it work on Windows?**

A: Yes! Dotenv-tools is cross-platform and works on Windows, macOS, and Linux.

**Q: Can I change the state file location?**

A: Yes, use the `--state-file` option:
```bash
load-dotenv --state-file /custom/path/.load_dotenv_state.json
```

**Q: What encoding is supported?**

A: UTF-8 is recommended and fully supported.

---

## Advanced Tips

### Using with Environment-Specific Files

```bash
# .env.development
DEBUG=true
LOG_LEVEL=debug

# .env.production
DEBUG=false
LOG_LEVEL=info
```

```bash
# For development
load-dotenv .env.development

# For production
load-dotenv .env.production
```

### Preloading Environment

```bash
# Set defaults before loading
export DEFAULT_DB_PORT=5432
load-dotenv
```

### Validation

After loading, validate your environment:

```bash
load-dotenv --verbose
# Check variables
env | grep DATABASE
env | grep API_KEY
```

### Cleanup Script

Create a cleanup script:

```bash
#!/bin/bash
# cleanup.sh
unload-dotenv --verbose
echo "Environment cleaned!"
```

Make it executable: `chmod +x cleanup.sh`

---

## Support

For issues, questions, or contributions:

- GitHub: https://github.com/LousyBook94/dotenv-tools
- Issues: https://github.com/LousyBook94/dotenv-tools/issues
- Email: lousybook94@gmail.com

---

**Author:** LousyBook01  \n**Version:** 0.0.1
