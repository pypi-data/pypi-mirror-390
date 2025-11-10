"""
Environment operations for utils_devops (env_ops module).

Provides utilities to manage .env files and system environment variables,
run commands with specific env settings, and safely update env files with
backup/restore support. This module is typed and exposes __all__ so IDEs
show a friendly API surface.

Notes:
- Uses python-dotenv for parsing/setting .env files.
- Uses files for backups and read/write operations.
- Uses systems.run for command execution with an injected environment.
- Logs actions via utils_devops.core.logger.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Dict, Optional, Union, List, Any
from dotenv import load_dotenv, dotenv_values, set_key as dotenv_set_key
from subprocess import CompletedProcess

from .logs import get_library_logger
from .files import backup_file, restore_file, write_file, read_file, FileOpsError
from .systems import run

log = get_library_logger()
# Public API for IDEs / help()
__all__ = [
    "EnvOpsError",
    "help",
    "load_env_file",
    "dump_env_file",
    "update_env_var",
    "remove_env_var",
    "backup_env_file",
    "restore_env_file",
    "get_system_env",
    "set_system_env",
    "export_system_to_env",
    "import_env_to_system",
    "run_with_env",
    "sync_env_to_system",
    "sync_system_to_env",
    "get_all_system_env",
]


class EnvOpsError(Exception):
    """Custom exception for environment operations failures."""
    pass


def help() -> None:
    """Print a short index of the env_ops API for interactive use.

    IDEs will pick up `__all__` and function docstrings for completion/help.
    """
    print(
        """
DevOps Utils — Environment Operations Module
Key functions:
EnvOpsError: Custom exception for environment operations failures.
help() -> None: Print a short index of the env_ops API for interactive use.
load_env_file(file_path: Union[str, Path]) -> Dict[str, str]: Load a .env file and return a dict of key->value.
dump_env_file(data: Dict[str, str], file_path: Union[str, Path], backup: bool = True) -> None: Write `data` to `file_path` as KEY=VALUE lines. Optionally back up original file.
update_env_var(key: str, value: str, file_path: Union[str, Path], backup: bool = True) -> None: Set or update a single key in a .env file using python-dotenv's set_key helper.
remove_env_var(key: str, file_path: Union[str, Path], backup: bool = True) -> None: Remove `key` from the .env file (if present).
backup_env_file(file_path: Union[str, Path]) -> Path: Create a backup of the .env file and return backup path.
restore_env_file(file_path: Union[str, Path], from_backup: Optional[Union[str, Path]] = None) -> None: Restore a .env file from backup (or the most recent one).
get_system_env(key: str, default: Optional[str] = None) -> Optional[str]: Get environment variable from os.environ (returns default if missing).
set_system_env(key: str, value: str) -> None: Set environment variable in the current process (os.environ).
export_system_to_env(file_path: Union[str, Path], keys: Optional[List[str]] = None) -> None: Export current process environment (or selected keys) to a .env file.
import_env_to_system(file_path: Union[str, Path], overwrite: bool = True) -> None: Load variables from .env into the process environment.
run_with_env(cmd: Union[str, List[str]], env_file: Optional[Union[str, Path]] = None, additional_env: Optional[Dict[str, str]] = None, **run_kwargs: Any) -> CompletedProcess: Run `cmd` with environment variables loaded from `env_file` and merged with additional_env.
sync_env_to_system(file_path: Union[str, Path], overwrite: bool = True) -> None: Alias for import_env_to_system.
sync_system_to_env(file_path: Union[str, Path], keys: Optional[List[str]] = None) -> None: Alias for export_system_to_env.
get_all_system_env() -> Dict[str, str]: Return a copy of the current process environment as a dict.
"""
    )


# ========================
# .env File Operations
# ========================


def load_env_file(file_path: Union[str, Path]) -> Dict[str, str]:
    """Load a .env file and return a dict of key->value.

    file_path: path to the .env file. If file doesn't exist returns an empty dict.
    """
    try:
        data = dotenv_values(file_path)
        log.info(f"Loaded .env from {file_path}: {len(data)} keys")
        # dotenv_values may return values as None for missing values; normalize to str
        return {k: (v if v is not None else "") for k, v in data.items()}
    except Exception as e:
        log.error(f"Failed to load .env {file_path}: {e}")
        raise EnvOpsError(f"Failed to load .env: {e}") from e


def dump_env_file(data: Dict[str, str], file_path: Union[str, Path], backup: bool = True) -> None:
    """Write `data` to `file_path` as KEY=VALUE lines. Optionally back up original file.

    Overwrites the target file.
    """
    file_path = Path(file_path)
    if backup and file_path.exists():
        backup_file(file_path)
    try:
        content = "\n".join(f"{k}={v}" for k, v in data.items())
        write_file(file_path, content)
        log.info(f"Dumped {len(data)} env vars to {file_path}")
    except FileOpsError as e:
        log.error(f"Failed to dump .env: {e}")
        raise EnvOpsError(f"Failed to dump .env: {e}") from e


def update_env_var(key: str, value: str, file_path: Union[str, Path], backup: bool = True) -> None:
    """Set or update a single key in a .env file using python-dotenv's set_key helper.

    If `file_path` doesn't exist it will be created.
    """
    file_path = Path(file_path)
    if backup and file_path.exists():
        backup_file(file_path)
    try:
        # dotenv_set_key returns tuple (success, new_value) on some implementations,
        # we'll rely on it to write to file. Ensure parent exists.
        file_path.parent.mkdir(parents=True, exist_ok=True)
        dotenv_set_key(str(file_path), key, value)
        log.info(f"Updated env var '{key}' in {file_path}")
    except Exception as e:
        log.error(f"Failed to update env var '{key}': {e}")
        raise EnvOpsError(f"Failed to update env var: {e}") from e


def remove_env_var(key: str, file_path: Union[str, Path], backup: bool = True) -> None:
    """Remove `key` from the .env file (if present)."""
    file_path = Path(file_path)
    if backup and file_path.exists():
        backup_file(file_path)
    try:
        data = load_env_file(file_path)
        data.pop(key, None)
        dump_env_file(data, file_path, backup=False)
        log.info(f"Removed env var '{key}' from {file_path}")
    except Exception as e:
        log.error(f"Failed to remove env var '{key}': {e}")
        raise EnvOpsError(f"Failed to remove env var: {e}") from e


def backup_env_file(file_path: Union[str, Path]) -> Path:
    """Create a backup of the .env file and return backup path."""
    return backup_file(file_path)


def restore_env_file(file_path: Union[str, Path], from_backup: Optional[Union[str, Path]] = None) -> None:
    """Restore a .env file from backup (or the most recent one)."""
    restore_file(file_path, from_backup)


# ========================
# System Environment Operations
# ========================


def get_system_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable from os.environ (returns default if missing)."""
    value = os.environ.get(key, default)
    log.debug(f"Got system env '{key}': {'[hidden]' if value else None}")
    return value


def set_system_env(key: str, value: str) -> None:
    """Set environment variable in the current process (os.environ)."""
    os.environ[key] = value
    log.info(f"Set system env '{key}'")


def export_system_to_env(file_path: Union[str, Path], keys: Optional[List[str]] = None) -> None:
    """Export current process environment (or selected keys) to a .env file."""
    data = {k: os.environ[k] for k in (keys or os.environ.keys())}
    dump_env_file(data, file_path)
    log.info(f"Exported {len(data)} system env vars to {file_path}")


def import_env_to_system(file_path: Union[str, Path], overwrite: bool = True) -> None:
    """Load variables from .env into the process environment.

    If overwrite is False existing os.environ keys are left untouched.
    """
    try:
        load_dotenv(dotenv_path=str(file_path), override=overwrite)
        log.info(f"Imported .env from {file_path} to system (overwrite={overwrite})")
    except Exception as e:
        log.error(f"Failed to import .env to system: {e}")
        raise EnvOpsError(f"Failed to import .env: {e}") from e


# ========================
# Command Execution with Env
# ========================


def run_with_env(
    cmd: Union[str, List[str]],
    env_file: Optional[Union[str, Path]] = None,
    additional_env: Optional[Dict[str, str]] = None,
    **run_kwargs: Any,
) -> CompletedProcess:
    """Run `cmd` with environment variables loaded from `env_file` and merged with additional_env.

    `run_kwargs` are forwarded to systems.run (cwd, elevated, dry_run, etc.). Returns CompletedProcess.
    """
    env = os.environ.copy()
    if env_file:
        env_file_data = load_env_file(env_file)
        env.update(env_file_data)
    if additional_env:
        env.update(additional_env)
    log.info(f"Running command with {len(env)} env vars")
    return run(cmd, env=env, **run_kwargs)


# Convenience aliases
sync_env_to_system = import_env_to_system
sync_system_to_env = export_system_to_env


def get_all_system_env() -> Dict[str, str]:
    """Return a copy of the current process environment as a dict."""
    data = dict(os.environ)
    log.debug(f"Got all system env: {len(data)} keys")
    return data
