import json
import os
import platform
import subprocess
import shutil
import click
import time
from typing import Optional
from importlib import metadata
from importlib.metadata import PackageNotFoundError


# -----------------------
# config dir helpers
# -----------------------
def get_config_dir() -> str:
    """
    Determine a sensible config directory cross-platform:

    Priority:
    1. SAHAJ_CONFIG_DIR env var (override for tests/CI)
    2. Windows: %APPDATA%/sahaj
    3. Unix: $XDG_CONFIG_HOME/sahaj (commonly ~/.config/sahaj)
    4. Fallback: ~/.sahaj
    """
    env_override = os.getenv("SAHAJ_CONFIG_DIR")
    if env_override:
        return os.path.expanduser(env_override)

    system = platform.system()
    if system == "Windows":
        appdata = os.getenv("APPDATA")
        if appdata:
            return os.path.join(os.path.expanduser(appdata), "sahaj")
        return os.path.expanduser("~/.sahaj")
    else:
        xdg = os.getenv("XDG_CONFIG_HOME")
        if xdg:
            return os.path.join(os.path.expanduser(xdg), "sahaj")
        return os.path.expanduser("~/.sahaj")


def get_config_path() -> str:
    cfg_dir = get_config_dir()
    return os.path.join(cfg_dir, "config.json")


# -----------------------
# utility functions
# -----------------------
def read_config() -> dict:
    path = get_config_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def write_config(data: dict) -> None:
    path = get_config_path()
    dirpath = os.path.dirname(path)
    os.makedirs(dirpath, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_version_string() -> str:
    try:
        # try lowercase distribution name (typical)
        v = metadata.version("sahaj")
    except PackageNotFoundError:
        # fallback to other names or local version marker
        try:
            v = metadata.version("SAHAJ")
        except PackageNotFoundError:
            v = "0+local"
    return v


# ---------------------------------------------------------------
# helpers required by the rundev, deploy and quickstart commands
# ---------------------------------------------------------------

QUICKSTART_MARKER = os.path.join(get_config_dir(), "quickstart_last.json")


def run_native(cmd, cwd=None, env=None, check=True):
    """Run a subprocess with native stdout/stderr so users see progress."""
    click.echo(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, env=env, check=check)


def get_compose_env(config_path: str, mode: str = "dev"):
    """Load config.json (repo-local or global) and return full env dict."""
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        try:
            config = read_config()
        except Exception:
            config = {}
    run_env = os.environ.copy()
    for k, v in config.items():
        key = str(k).upper().replace("-", "_").replace(" ", "_")
        run_env[key] = "" if v is None else str(v)
    run_env["SAHAJ_RUN_ENV"] = mode
    return run_env


def run_repo_script(target_path: str, base_script: str, run_env: dict):
    """
    Run platform-appropriate script: .bat on Windows, .sh on Unix.
    Returns CompletedProcess or raises CalledProcessError.
    """
    system = platform.system()
    if system == "Windows":
        script_path = os.path.join(target_path, base_script + ".bat")
        if not os.path.exists(script_path):
            raise FileNotFoundError(script_path)
        return run_native(["cmd", "/c", script_path], cwd=target_path, env=run_env)
    else:
        script_path = os.path.join(target_path, base_script + ".sh")
        if not os.path.exists(script_path):
            raise FileNotFoundError(script_path)
        bash = shutil.which("bash") or shutil.which("sh")
        if not bash:
            raise FileNotFoundError("bash/sh")
        return run_native([bash, script_path], cwd=target_path, env=run_env)


def write_quickstart_marker(compose_path: str):
    try:
        os.makedirs(os.path.dirname(QUICKSTART_MARKER), exist_ok=True)
        with open(QUICKSTART_MARKER, "w", encoding="utf-8") as f:
            json.dump({"compose_path": compose_path, "ts": int(time.time())}, f)
        click.echo(f"Created quickstart marker: {QUICKSTART_MARKER}")
    except Exception as e:
        click.echo(f"Warning: failed to write quickstart marker: {e}")


def read_quickstart_marker() -> Optional[str]:
    if not os.path.exists(QUICKSTART_MARKER):
        return None
    try:
        with open(QUICKSTART_MARKER, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("compose_path")
    except Exception:
        return None


def _docker_list_lines(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return []
    return [line.strip() for line in res.stdout.splitlines() if line.strip()]


def _project_from_path(path):
    return os.path.basename(os.path.abspath(path)).lower()
