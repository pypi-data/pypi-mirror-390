"""Command-line interface for dotenv-tools.

Provides load-dotenv, unload-dotenv, and set-dotenv commands.
"""

import os
from pathlib import Path
from typing import Optional

import click

from .core import LoadDotenv, find_dotenv_file, LoadDotenvError, LoadDotenvFileNotFound
from .tracker import Tracker
from .setter import SetDotenv, find_or_create_dotenv_file, SetDotenvError, SetDotenvFileNotFound


# Default state file location
DEFAULT_STATE_FILE = Path.home() / '.load_dotenv_state.json'


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context):
    """Dotenv-tools: Manage environment variables in .env files.

    This tool provides three commands:

    - load-dotenv: Load variables from a .env file into the environment
    - unload-dotenv: Remove all loaded variables from the environment
    - set-dotenv: Set, update, or remove variables in .env files

    For more information, see USAGE.md
    """
    if ctx.invoked_subcommand is None:
        click.echo("Use 'load-dotenv --help' for usage information")


@cli.command()
@click.argument('file', type=Path, required=False)
@click.option(
    '--override', '-o',
    is_flag=True,
    help='Override existing environment variables'
)
@click.option(
    '--state-file',
    type=Path,
    default=DEFAULT_STATE_FILE,
    help=f'Path to state file (default: {DEFAULT_STATE_FILE})'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Show detailed output'
)
def load_dotenv(
    file: Optional[Path],
    override: bool,
    state_file: Path,
    verbose: bool
):
    """Load environment variables from a .env file.

    FILE: Path to .env file (optional). If not provided, searches for .env
    starting from the current directory.

    Examples:

        load-dotenv

        load-dotenv /path/to/custom.env

        load-dotenv --override /path/to/.env
    """
    try:
        # Find the .env file
        if file is None:
            env_file = find_dotenv_file()
            if verbose:
                click.echo(f"Found .env file: {env_file}")
        else:
            env_file = file
            if not env_file.exists():
                raise click.ClickException(f"File not found: {env_file}")

        # Initialize loader
        loader = LoadDotenv(env_file)

        # Load variables
        if verbose:
            click.echo(f"Loading environment variables from {env_file}...")

        variables_to_set = loader.load(override=override)

        if not variables_to_set:
            if verbose:
                click.echo("No variables to load.")
            return

        # Track and set variables
        tracker = Tracker(state_file)
        tracker.snapshot_environment()

        loaded_count = tracker.load_variables(variables_to_set)

        if verbose:
            for key, value in variables_to_set.items():
                # Hide sensitive values
                if any(sensitive in key.lower() for sensitive in
                       ['password', 'secret', 'key', 'token', 'auth']):
                    click.echo(f"  {key} = *****")
                else:
                    click.echo(f"  {key} = {value}")

        if loaded_count > 0:
            click.echo(f"\n[OK] Successfully loaded {loaded_count} environment variables")
        else:
            click.echo(f"\n[INFO] No new variables loaded")

    except LoadDotenvFileNotFound as e:
        raise click.ClickException(str(e))
    except LoadDotenvError as e:
        raise click.ClickException(f"Error loading .env file: {e}")
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {e}")


@cli.command()
@click.option(
    '--state-file',
    type=Path,
    default=DEFAULT_STATE_FILE,
    help=f'Path to state file (default: {DEFAULT_STATE_FILE})'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Show detailed output'
)
@click.option(
    '--force', '-f',
    is_flag=True,
    help='Unload without confirmation'
)
def unload_dotenv(
    state_file: Path,
    verbose: bool,
    force: bool
):
    """Remove all environment variables loaded by this tool.

    This command will remove all variables that were loaded by load-dotenv
    and are currently tracked in the state file.

    Examples:

        unload-dotenv

        unload-dotenv --verbose

        unload-dotenv --force
    """
    # Load tracking state
    tracker = Tracker(state_file)
    loaded = tracker.load_state()

    if not loaded:
        click.echo("No environment variables to unload.")
        return

    count, variables = tracker.get_status()

    if verbose:
        click.echo("The following environment variables will be removed:")
        for var in sorted(variables):
            click.echo(f"  - {var}")

    # Confirmation
    if not force:
        if not click.confirm(f'\nUnload {count} environment variables?'):
            click.echo("Cancelled.")
            return

    # Unload
    unloaded = tracker.unload_all()

    if verbose and unloaded > 0:
        click.echo(f"\nUnloaded variables:")
        for var in sorted(variables):
            click.echo(f"  - {var}")

    click.echo(f"\n[OK] Successfully unloaded {unloaded} environment variables")


@cli.command()
@click.argument('key_value', nargs=-1, required=False)
@click.option(
    '--file', '-f',
    type=Path,
    help='Path to .env file (default: finds or creates .env in current directory)'
)
@click.option(
    '--remove', '-r',
    is_flag=True,
    help='Remove the specified variable'
)
@click.option(
    '--operator', '-o',
    type=click.Choice(['=', ':=', '+=', '?='], case_sensitive=False),
    default='=',
    help='Assignment operator (default: =)'
)
@click.option(
    '--edit', '-e',
    is_flag=True,
    help='Edit the .env file with your default editor'
)
@click.option(
    '--editor',
    type=str,
    help='Editor to use for editing (default: $EDITOR or $VISUAL)'
)
@click.option(
    '--list', '-l',
    is_flag=True,
    help='List all variables in the .env file'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Show detailed output'
)
def set_dotenv(
    key_value: tuple,
    file: Optional[Path],
    remove: bool,
    operator: str,
    edit: bool,
    editor: Optional[str],
    list: bool,
    verbose: bool
):
    """Set, update, or remove environment variables in .env files.

    This command supports multiple modes:

    1. Set a variable:
       set-dotenv KEY VALUE        # Sets KEY=value
       set-dotenv KEY=VALUE        # Sets KEY=VALUE
       set-dotenv KEY:=VALUE       # Sets KEY:=VALUE

    2. Remove a variable:
       set-dotenv --remove KEY

    3. Edit the file:
       set-dotenv --edit
       set-dotenv --edit --editor vim

    4. List all variables:
       set-dotenv --list

    Examples:

        set-dotenv PORT 3000
        set-dotenv API_KEY=secret123
        set-dotenv --remove API_KEY
        set-dotenv --edit
        set-dotenv --list
        set-dotenv --file /path/to/.env PORT 8080
    """
    try:
        # Find the .env file
        if file is None:
            env_file = find_or_create_dotenv_file()
            if verbose:
                click.echo(f"Using .env file: {env_file}")
        else:
            env_file = file
            if not env_file.exists():
                # Create file if it doesn't exist
                env_file.touch()

        # Initialize setter
        setter = SetDotenv(env_file)

        # Handle --edit flag
        if edit:
            if verbose:
                editor_name = editor or os.environ.get('EDITOR', os.environ.get('VISUAL', 'vi'))
                click.echo(f"Editing {env_file} with {editor_name}...")
            setter.edit_file(editor)
            if verbose:
                click.echo("[OK] Edit complete")
            return

        # Handle --list flag
        if list:
            variables = setter.list_variables()
            if not variables:
                click.echo("No variables found in .env file.")
                return

            click.echo(f"\nVariables in {env_file}:")
            for key, op, value in variables:
                # Hide sensitive values
                if any(sensitive in key.lower() for sensitive in
                       ['password', 'secret', 'key', 'token', 'auth']):
                    click.echo(f"  {key} {op} *****")
                else:
                    click.echo(f"  {key} {op} {value}")
            click.echo(f"\nTotal: {len(variables)} variables")
            return

        # Handle --remove flag
        if remove:
            if not key_value:
                raise click.ClickException("Please specify a variable name to remove")
            if len(key_value) > 1:
                raise click.ClickException("Only one variable can be removed at a time")

            key = key_value[0]
            removed = setter.remove_variable(key)

            if removed:
                click.echo(f"[OK] Removed variable '{key}' from {env_file}")
            else:
                click.echo(f"Variable '{key}' not found in {env_file}")
            return

        # Handle setting variables
        if not key_value:
            raise click.ClickException(
                "Please specify a variable to set. Use --help for usage information."
            )

        # Parse arguments
        if len(key_value) == 1:
            # Check if it contains '=' (KEY=VALUE format)
            if '=' in key_value[0]:
                parts = key_value[0].split('=', 1)
                key = parts[0].strip()
                value = parts[1].strip()
                # Infer operator from the assignment
                if key_value[0].startswith(key + ':='):
                    operator = ':='
                elif key_value[0].startswith(key + '+='):
                    operator = '+='
                elif key_value[0].startswith(key + '?='):
                    operator = '?='
            else:
                raise click.ClickException(
                    f"Invalid format. Use 'set-dotenv KEY VALUE' or 'set-dotenv KEY=VALUE'"
                )
        elif len(key_value) == 2:
            key = key_value[0]
            value = key_value[1]
        else:
            raise click.ClickException("Too many arguments")

        # Set the variable
        setter.set_variable(key, value, operator)

        if verbose:
            click.echo(f"[OK] Set {key} {operator} {value} in {env_file}")
        else:
            click.echo(f"[OK] Updated {key}")

    except (SetDotenvError, SetDotenvFileNotFound) as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {e}")


if __name__ == '__main__':
    cli()
