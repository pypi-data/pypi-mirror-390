# src/utils_devops/core/systems.py
"""
System Operations Module

... (docstring kept as before; trimmed here for brevity)
"""
from __future__ import annotations

import os
import sys
import platform
import subprocess
import shutil
import time
import socket
import getpass
import ctypes  # For Windows admin check
from typing import Optional, List, Dict, Union, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm

from .logs import get_library_logger  # Adjust if different

logger = get_library_logger()
console = Console()

DEFAULT_SYSTEM_TIMEZONE = "Asia/Tehran"  # Change this to your preferred default

# cached sudo password living in process memory only
_SUDO_PASSWORD: Optional[str] = None

# Public API for IDEs / help()
__all__ = [
    "help",
    # Environment Detection
    "is_windows",
    "is_linux",
    "is_docker",
    "is_root",
    # Process Management
    "check_process_running",
    "kill_process",
    # Waiting Functions
    "wait_for_file",
    "wait_for_port",
    "wait_command_success",
    "retry_cmd",
    # Port Operations
    "check_port_open",
    # User Interaction
    "ask_yes_no",
    "prompt_input",
    "ask_password",
    "confirm_action",
    "ask_choice_list",
    # Command Execution
    "run",
    "exec",
    # Sudo helpers
    "set_sudo_password",
    "clear_sudo_password",
    # Access & Elevation
    "command_exists",
    # Package Management
    "install_chocolatey",
    "install_package",
    "add_apt_repository",
    # Version & Location
    "find_command_location",
    "get_command_version",
    # System Metrics
    "get_cpu_usage",
    "get_memory_info",
    "get_disk_usage",
    # PowerShell (Windows)
    "run_powershell",
    # Utilities
    "list_directory_recursive",
    "readlink_f",
    # Timezone helpers
    "set_system_timezone",
    "get_system_timezone",
    "setup_tehran_timezone",
    # Service Reload
    "reload_service",
    # constants
    "DEFAULT_SYSTEM_TIMEZONE",
]

# ---------------------
# Helper / help
# ---------------------
def help() -> None:
    """Print a brief index of available functions in this module."""
    print(
    """
    System Operations Module - Usage Reference
    ==========================================

    Environment Detection
    ---------------------
    is_windows() -> bool
        Return True if running on Windows OS.
    is_linux() -> bool
        Return True if running on Linux OS.
    is_docker() -> bool
        Return True if running inside a Docker container (Linux only).
    is_root() -> bool
        Return True if process has administrative/root privileges.

    Process Management
    ------------------
    check_process_running(pattern: str) -> bool
        Check if any running process name or command line contains `pattern`.
    kill_process(pattern: str) -> None
        Kill all processes matching `pattern`. Raises ValueError if none found.

    Waiting Functions
    -----------------
    wait_for_file(file_path: str, timeout: int = 30) -> bool
        Wait up to `timeout` seconds for a file to appear. Return True if found.
    wait_for_port(host: str = "localhost", port: int = 80, timeout: int = 30) -> bool
        Wait up to `timeout` seconds for a TCP port to become open.
    wait_command_success(cmd: str, retries: int = 5, delay: int = 1) -> None
        Retry running a shell command until success or retries exhausted.
    retry_cmd = wait_command_success
        Alias for `wait_command_success`.

    Port Operations
    ----------------
    check_port_open(host: str = "localhost", port: int = 80) -> bool
        Return True if port is open on given host.

    User Interaction
    ----------------
    ask_yes_no(prompt: str = "Confirm (y/n)?") -> bool
        Prompt user with yes/no question. Return True for “yes”.
    prompt_input(prompt: str = "Enter:") -> str
        Ask user for text input. Return entered string.
    ask_password(prompt: str = "Password:") -> str
        Ask for password securely (no echo). Return entered string.
    confirm_action(action_desc: str) -> None
        Warn user about an action and ask confirmation. Raise RuntimeError if cancelled.
    ask_choice_list(prompt: str, options: list[str]) -> str
        Display numbered list of `options` and return chosen one.

    Command Execution
    -----------------
    run(
        cmd: str | list[str],
        shell: bool | None = None,
        cwd: PathLike | None = None,
        env: dict[str, str] | None = None,
        no_die: bool = False,
        dry_run: bool = False,
        elevated: bool = False,
        capture: bool = True
    ) -> subprocess.CompletedProcess
        Run a command safely with logging, optional sudo/UAC elevation, and output capture.
        - If elevated=True: will use cached sudo password or prompt once.
        - Returns CompletedProcess with .stdout, .stderr, .returncode.

    exec(
        cmd: str | list[str],
        shell: bool | None = None,
        cwd: PathLike | None = None,
        env: dict[str, str] | None = None,
        no_die: bool = False,
        dry_run: bool = False,
        elevated: bool = False,
        capture: bool = True,
        show_output: bool = True
    ) -> subprocess.CompletedProcess
        Same as `run()` but prints command, stdout, stderr, and return code nicely.

    Access & Elevation
    ------------------
    command_exists(cmd: str) -> bool
        Return True if command is found in system PATH.

    Package Management
    ------------------
    install_chocolatey() -> None
        Install Chocolatey on Windows if not already installed.
    install_package(package_name: str, update_first: bool = True) -> None
        Install package via apt (Linux) or Chocolatey (Windows).
    add_apt_repository(repo: str, update_after: bool = True) -> None
        Add an APT repository (Linux). Optionally run `apt update` after.

    Version & Location
    ------------------
    find_command_location(cmd: str) -> str | None
        Return full path to command, or None if not found.
    get_command_version(cmd: str) -> str | None
        Return command version output if available.
    readlink_f(path: str) -> str
        Resolve all symlinks and return canonical absolute path.

    System Metrics
    --------------
    get_cpu_usage() -> float
        Return current system CPU usage percentage.
    get_memory_info() -> dict
        Return memory stats: {"total", "available", "used", "percent"}.
    get_disk_usage(path: str = "/") -> dict
        Return disk stats for given path: {"total", "used", "free", "percent"}.

    PowerShell (Windows)
    --------------------
    run_powershell(cmd: str, elevated: bool = False) -> int
        Execute PowerShell command. Return exit code.

    Utilities
    ---------
    list_directory_recursive(path: str = ".", detailed: bool = False) -> None
        Recursively list directory tree. Show permissions/sizes if detailed=True.

    System Timezone
    ---------------
    set_system_timezone(tz: str | None = None, confirm: bool = True) -> None
        Set system timezone (default: Asia/Tehran). Uses `timedatectl` or fallback link.
    get_system_timezone() -> str
        Return current system timezone as string.
    setup_tehran_timezone(confirm: bool = True) -> None
        Shortcut to set timezone to Asia/Tehran.

    Service Management
    ------------------
    reload_service(service_cmd: str | list[str], test_cmd: str | list[str]) -> bool
        Run `test_cmd`, and if success, reload service with `service_cmd`.
        Return True if both succeed, False otherwise.

    Constants
    ---------
    DEFAULT_SYSTEM_TIMEZONE = "Asia/Tehran"
        Default timezone used in all system timezone functions.
    """
    )


# -------------------------------------------------
# Secure sudo / elevation handling (improved)
# -------------------------------------------------
def clear_sudo_password() -> None:
    """Erase the cached sudo password from memory (public)."""
    global _SUDO_PASSWORD
    _SUDO_PASSWORD = None
    logger.debug("Cleared cached sudo password.")


def set_sudo_password(pw: str) -> None:
    """Set the sudo password programmatically (for automation/testing)."""
    global _SUDO_PASSWORD
    _SUDO_PASSWORD = pw
    logger.debug("Sudo password set programmatically (in-memory only).")


def _get_sudo_password(prompt: str = "Enter sudo password: ") -> str:
    """
    Ask for the sudo password once per process (cached in-memory).
    Will not re-prompt unless the cache has been cleared (clear_sudo_password()).

    Note: the password is kept only in process memory and never written to disk.
    """
    global _SUDO_PASSWORD
    if _SUDO_PASSWORD is None:
        # loop to avoid accidental empty password entry, but only a couple tries
        pw = getpass.getpass(prompt)
        # Accept empty password if user enters it explicitly (some sudo setups allow it),
        # but warn so user understands risks.
        if pw == "":
            logger.warning("Empty sudo password entered (are you sure?).")
        _SUDO_PASSWORD = pw
    else:
        logger.debug("Using cached sudo password.")
    return _SUDO_PASSWORD


# ========================
# Command Execution
# ========================

def run(
    cmd: Union[str, List[str]],
    *,
    shell: Optional[bool] = None,
    cwd: Optional[os.PathLike] = None,
    env: Optional[Dict[str, str]] = None,
    no_die: bool = False,
    dry_run: bool = False,
    elevated: bool = False,
    capture: bool = True,
) -> subprocess.CompletedProcess:
    """
    Core run() – smart about shell and elevation.

    If elevated=True on Unix, the cached sudo password is used (prompted once per process).
    If sudo authentication fails we clear the cached password and raise a CalledProcessError
    with a helpful message.

    Returns subprocess.CompletedProcess
    """
    if shell is None:
        shell = isinstance(cmd, str)

    # Normalize cmd into either str or list form for subprocess
    if isinstance(cmd, (list, tuple)):
        cmd_str = subprocess.list2cmdline(cmd)
        cmd_list: Union[List[str], str] = list(cmd)
    else:
        cmd_str = str(cmd)
        cmd_list = cmd_str if shell else [cmd_str]

    if dry_run:
        logger.info(f"[DRY-RUN] {cmd_str}")
        return subprocess.CompletedProcess(cmd_list if not shell else cmd_str, 0, stdout="", stderr="")

    stdin_input: Optional[str] = None
    use_list: Union[List[str], str] = cmd_list

    if elevated:
        if is_windows():
            # For Windows, use Start-Process -Verb RunAs via powershell
            ps = f"Start-Process -Verb RunAs -FilePath powershell -ArgumentList '-NoProfile','-Command','{cmd_str}' -Wait -PassThru"
            use_list = ["powershell", "-NoProfile", "-Command", ps]
            shell = False
        else:
            # Unix: prepend sudo -S and provide password via stdin
            pw = _get_sudo_password()
            # Build command list safely (avoid shell where possible)
            if isinstance(cmd, (list, tuple)):
                base_list = list(cmd)
            else:
                # if original was a string and shell=True, pass the string to sudo as a single shell invocation
                base_list = [cmd_str] if shell else [cmd_str]
            use_list = ["sudo", "-S"] + base_list
            stdin_input = (pw + "\n") if pw is not None else None
            shell = False  # we pass a list to Popen

    # Log the final command representation (avoid logging password)
    try:
        if isinstance(use_list, list):
            logger.debug(f"Executing (list): {' '.join(use_list)}")
        else:
            logger.debug(f"Executing (shell): {use_list}")

        proc = subprocess.Popen(
            use_list if not shell else (cmd_str),
            cwd=str(cwd) if cwd else None,
            env=env,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            stdin=subprocess.PIPE if stdin_input is not None else None,
            text=True,
            shell=shell,
        )

        if stdin_input is not None and proc.stdin:
            # write password and flush; do not keep password in logs
            try:
                proc.stdin.write(stdin_input)
                proc.stdin.flush()
                proc.stdin.close()
            except Exception:
                # If writing fails, ensure we close and continue to wait for process
                try:
                    proc.stdin.close()
                except Exception:
                    pass

        stdout, stderr = proc.communicate()
        rc = proc.returncode

        result = subprocess.CompletedProcess(
            use_list if not shell else cmd_str,
            rc,
            stdout=stdout or "",
            stderr=stderr or "",
        )

        if rc == 0:
            logger.info(f"Command succeeded (rc={rc})")
        else:
            # If elevated on Unix and sudo-auth failure detected, clear cache and raise helpful error
            if elevated and not is_windows():
                lowerr = (stderr or "").lower()
                # Common sudo auth failure tokens
                auth_tokens = [
                    "incorrect password",
                    "authentication failure",
                    "authentication token manipulation error",
                    "sorry,",
                    "sudo: 1 incorrect password attempt",
                    "sudo: a password is required",
                    "pam_authenticate",
                ]
                if any(tok in lowerr for tok in auth_tokens):
                    # Clear cached password so user isn't forced to keep using wrong one
                    clear_sudo_password()
                    logger.error("sudo authentication failed. Cached sudo password cleared.")
                    # Raise with stderr included for context
                    raise subprocess.CalledProcessError(rc, use_list if not shell else cmd_str, output=stdout, stderr=stderr)

            # General logging for failure
            logger.error(f"Command failed (rc={rc}) – {stderr.strip() if stderr else ''}")

        if rc != 0 and not no_die:
            raise subprocess.CalledProcessError(rc, use_list if not shell else cmd_str, output=stdout, stderr=stderr)

        return result

    except subprocess.CalledProcessError:
        # Re-raise CalledProcessError so callers can handle; do not clear cached password here
        raise

    except Exception as e:
        logger.exception(f"Unexpected error running command: {e}")
        raise


# -------------------------------------------------
# Exec helper – shows command + output + logs
# -------------------------------------------------
def exec(
    cmd: Union[str, List[str]],
    *,
    shell: Optional[bool] = None,
    cwd: Optional[os.PathLike] = None,
    env: Optional[Dict[str, str]] = None,
    no_die: bool = False,
    dry_run: bool = False,
    elevated: bool = False,
    capture: bool = True,
    show_output: bool = True,
) -> subprocess.CompletedProcess:
    """
    Run a command and show output.

    - If `cmd` is **str** → runs in shell (like bash)
    - If `cmd` is **list** → runs safely (no shell)
    - `shell=True` only when needed
    """
    # Auto-detect shell mode
    if shell is None:
        shell = isinstance(cmd, str)

    # Forward to run()
    result = run(
        cmd,
        shell=shell,
        cwd=cwd,
        env=env,
        no_die=no_die,
        dry_run=dry_run,
        elevated=elevated,
        capture=capture,
    )

    # Show output
    if not dry_run and show_output:
        cmd_str = cmd if isinstance(cmd, str) else subprocess.list2cmdline(cmd)

        console.print(f"\n[bold cyan]>>> {cmd_str}[/bold cyan]")

        if result.stdout:
            console.print(f"[green]STDOUT:[/green]\n{result.stdout.rstrip()}")

        if result.stderr:
            console.print(f"[red]STDERR:[/red]\n{result.stderr.rstrip()}")

        rc_color = "green" if result.returncode == 0 else "red"
        console.print(f"[{rc_color}]Return code: {result.returncode}[/{rc_color}]\n")

    return result


# ========================
# Section: System Timezone Management
# (unchanged except forwarded to run)
# ========================
def set_system_timezone(tz: Optional[str] = None, confirm: bool = True) -> None:
    if tz is None:
        tz = DEFAULT_SYSTEM_TIMEZONE
        logger.info(f"Using default timezone: {tz}")

    if confirm:
        confirm_action(f"change system timezone to {tz}")

    if is_windows():
        win_name = "Iran Standard Time" if tz == "Asia/Tehran" else tz.replace("/", " ")
        cmd = ["tzutil", "/s", win_name]
    else:
        if command_exists("timedatectl"):
            cmd = ["timedatectl", "set-timezone", tz]
        else:
            cmd = ["ln", "-sf", f"/usr/share/zoneinfo/{tz}", "/etc/localtime"]

    run(cmd, elevated=True)
    logger.info(f"System timezone set to: {tz}")


def get_system_timezone() -> str:
    try:
        if is_windows():
            res = run(["tzutil", "/g"], capture=True)
            return res.stdout.strip().strip('"')
        else:
            if command_exists("timedatectl"):
                res = run(
                    ["timedatectl", "show", "--property=Timezone", "--value"],
                    capture=True,
                )
                return res.stdout.strip()
            else:
                try:
                    with open("/etc/timezone", "r") as f:
                        return f.read().strip()
                except FileNotFoundError:
                    try:
                        link = os.readlink("/etc/localtime")
                        return link.split("zoneinfo/")[-1]
                    except Exception:
                        return "Unknown"
    except Exception as e:
        logger.warning(f"Failed to read system timezone: {e}")
        return "Unknown"


def setup_tehran_timezone(confirm: bool = True) -> None:
    set_system_timezone(tz=DEFAULT_SYSTEM_TIMEZONE, confirm=confirm)


# ========================
# Environment Detection
# ========================
def is_windows() -> bool:
    return platform.system() == "Windows"


def is_linux() -> bool:
    return platform.system() == "Linux"


def is_docker() -> bool:
    if not is_linux():
        return False
    try:
        with open("/proc/1/cgroup", "r") as f:
            content = f.read()
            return "docker" in content or "/docker/" in content
    except Exception as e:
        logger.debug(f"Failed to check Docker: {e}")
        return False


def is_root() -> bool:
    if is_windows():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            logger.debug(f"Failed to check admin on Windows: {e}")
            return False
    else:
        return os.getuid() == 0


# ========================
# Process Management (psutil)
# ========================
import psutil  # required dependency

def check_process_running(pattern: str) -> bool:
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        cmdline = " ".join(proc.info.get("cmdline") or [])
        name = proc.info.get("name") or ""
        if pattern in name or pattern in cmdline:
            return True
    return False


def kill_process(pattern: str) -> None:
    killed = False
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        cmdline = " ".join(proc.info.get("cmdline") or [])
        name = proc.info.get("name") or ""
        if pattern in name or pattern in cmdline:
            try:
                proc.kill()
                killed = True
            except psutil.NoSuchProcess:
                pass
            except Exception as e:
                logger.error(f"Failed to kill process {proc.pid}: {e}")
                raise
    if not killed:
        raise ValueError(f"No process matching '{pattern}' found to kill.")


# ========================
# Waiting Functions
# ========================
def wait_for_file(file_path: str, timeout: int = 30) -> bool:
    start = time.time()
    while not os.path.exists(file_path):
        if time.time() - start > timeout:
            logger.error(f"Timeout waiting for file: {file_path}")
            return False
        time.sleep(1)
    logger.info(f"File appeared: {file_path}")
    return True


def wait_for_port(host: str = "localhost", port: int = 80, timeout: int = 30) -> bool:
    start = time.time()
    while not check_port_open(host, port):
        if time.time() - start > timeout:
            logger.error(f"Timeout waiting for {host}:{port}")
            return False
        time.sleep(1)
    logger.info(f"Port open: {host}:{port}")
    return True


def wait_command_success(cmd: str, retries: int = 5, delay: int = 1) -> None:
    for attempt in range(1, retries + 1):
        try:
            subprocess.check_call(cmd, shell=True)
            logger.info(f"Command succeeded on attempt {attempt}: {cmd}")
            return
        except subprocess.CalledProcessError as e:
            logger.warning(f"Attempt {attempt} failed: {cmd} (rc={e.returncode})")
            time.sleep(delay)
    raise RuntimeError(f"Command failed after {retries} retries: {cmd}")


retry_cmd = wait_command_success


# ========================
# Port / User / Package / Utilities / Metrics / Service Reload
# (unchanged from prior implementation except small logging tweaks)
# ========================
def check_port_open(host: str = "localhost", port: int = 80) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((host, port))
        return result == 0
    finally:
        sock.close()


def ask_yes_no(prompt: str = "Confirm (y/n)?") -> bool:
    return Confirm.ask(f"[magenta]{prompt}[/magenta]")


def prompt_input(prompt: str = "Enter:") -> str:
    return Prompt.ask(f"[magenta]{prompt}[/magenta]")


def ask_password(prompt: str = "Password:") -> str:
    console.print(f"[magenta]{prompt}[/magenta]", end=" ")
    return getpass.getpass("")


def confirm_action(action_desc: str) -> None:
    logger.warning(f"About to {action_desc}. Continue?")
    if not ask_yes_no():
        raise RuntimeError("Action cancelled by user.")


def ask_choice_list(prompt: str = "Choose:", options: Optional[List[str]] = None) -> str:
    if options is None:
        options = []
    for i, opt in enumerate(options, 1):
        console.print(f"{i}) {opt}")
    choice = Prompt.ask(f"[magenta]{prompt}[/magenta]")
    if choice.isdigit() and 1 <= int(choice) <= len(options):
        return options[int(choice) - 1]
    raise ValueError("Invalid choice.")


def command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def install_chocolatey() -> None:
    if not is_windows():
        raise NotImplementedError("Chocolatey is for Windows only.")
    if command_exists("choco"):
        logger.info("Chocolatey already installed.")
        return
    ps_cmd = "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    run(f"powershell -Command \"{ps_cmd}\"", elevated=True)
    logger.info("Chocolatey installed.")


def install_package(package_name: str, update_first: bool = True) -> None:
    if is_windows():
        install_chocolatey()
        run(f"choco install {package_name} -y", elevated=True)
    elif is_linux():
        if update_first:
            run("apt update", elevated=True)
        run(f"apt install {package_name} -y", elevated=True)
    else:
        raise NotImplementedError("Unsupported OS for package installation.")


def add_apt_repository(repo: str, update_after: bool = True) -> None:
    if not is_linux():
        raise NotImplementedError("APT repositories are for Linux only.")
    run(f"add-apt-repository {repo} -y", elevated=True)
    if update_after:
        run("apt update", elevated=True)


def find_command_location(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def get_command_version(cmd: str) -> Optional[str]:
    if not command_exists(cmd):
        return None
    try:
        res = run([cmd, "--version"], capture=True)
        return res.stdout.strip()
    except Exception as e:
        logger.debug(f"Failed to get version for {cmd}: {e}")
        return None


def readlink_f(path: str) -> str:
    try:
        real_path = os.path.realpath(path)
        logger.debug(f"Resolved path {path} to {real_path}")
        return real_path
    except Exception as e:
        logger.error(f"Failed to resolve path {path}: {e}")
        raise RuntimeError(f"Failed to resolve path {path}: {e}") from e


def list_directory_recursive(path: str = ".", detailed: bool = False) -> None:
    for root, dirs, files in os.walk(path):
        console.print(f"{root}:")
        if detailed:
            total_size = 0
            for name in dirs + files:
                full = os.path.join(root, name)
                try:
                    stat = os.stat(full)
                    mode = oct(stat.st_mode)[-4:]  # Simplified permissions
                    size = stat.st_size
                    total_size += size if os.path.isfile(full) else 0
                    console.print(f"{mode} {size:8} {name}")
                except Exception as e:
                    console.print(f"Error accessing {name}: {e}")
            console.print(f"total {total_size}")
        else:
            for name in dirs + files:
                console.print(name)
        console.print("")


def get_cpu_usage() -> float:
    return psutil.cpu_percent(interval=1)


def get_memory_info() -> Dict[str, Union[int, float]]:
    mem = psutil.virtual_memory()
    return {"total": mem.total, "available": mem.available, "used": mem.used, "percent": mem.percent}


def get_disk_usage(path: str = "/") -> Dict[str, Union[int, float]]:
    disk = psutil.disk_usage(path)
    return {"total": disk.total, "used": disk.used, "free": disk.free, "percent": disk.percent}


def run_powershell(cmd: str, elevated: bool = False) -> int:
    if not is_windows():
        raise NotImplementedError("PowerShell is for Windows only.")
    ps_cmd = f"powershell -Command \"{cmd}\""
    res = run(ps_cmd, elevated=elevated)
    return res.returncode


def reload_service(service_cmd: Union[List[str], str], test_cmd: Union[List[str], str]) -> bool:
    logger.info(f"Testing with: {test_cmd}")
    try:
        test_res = run(test_cmd, capture=True, no_die=True)
        if test_res.returncode != 0:
            logger.error(f"Test failed (rc={test_res.returncode}): {test_res.stderr.strip()}")
            return False
        logger.info("Test succeeded.")

        logger.info(f"Reloading with: {service_cmd}")
        reload_res = run(service_cmd, elevated=True, capture=True)
        if reload_res.returncode == 0:
            logger.info("Reload succeeded.")
            return True
        else:
            logger.error(f"Reload failed (rc={reload_res.returncode}): {reload_res.stderr.strip()}")
            return False
    except Exception as e:
        logger.error(f"Reload process failed: {e}")
        return False
