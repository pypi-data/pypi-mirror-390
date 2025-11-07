from __future__ import annotations

import os
import sys
import subprocess
from typing import List, Optional, Mapping
from rich.console import Console
from rich.status import Status

console = Console()
VERBOSE: bool = False


def set_verbose(v: bool) -> None:
    global VERBOSE
    VERBOSE = v


def info(message: str) -> None:
    """Print informational logs only when verbose mode is enabled."""
    if VERBOSE:
        console.print(message)


def run(cmd: List[str] | str, cwd: Optional[str] = None, env: Optional[Mapping[str, str]] = None, shell: bool = False, force_stream: bool = False) -> int:
    """Run a subprocess, streaming output to console.

    Returns the process return code.
    """
    cmd_str = ' '.join(cmd) if isinstance(cmd, list) else cmd
    if VERBOSE or force_stream:
        console.log(f"[bold cyan]$ {cmd_str}")
        try:
            proc = subprocess.Popen(
                cmd if isinstance(cmd, list) else cmd,
                cwd=cwd,
                env=env,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            assert proc.stdout is not None
            for line in proc.stdout:
                console.print(line.rstrip())
            proc.wait()
            return proc.returncode or 0
        except FileNotFoundError:
            console.print("[red]Command not found")
            return 127
    else:
        # Silent mode with pretty spinner; capture output and only show on failure
        try:
            with console.status("[cyan]Running...", spinner="dots") as status:
                proc = subprocess.run(
                    cmd if isinstance(cmd, list) else cmd,
                    cwd=cwd,
                    env=env,
                    shell=shell,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    check=False,
                )
                rc = proc.returncode or 0
                if rc != 0 and proc.stdout:
                    console.print(proc.stdout)
                return rc
        except FileNotFoundError:
            console.print("[red]Command not found")
            return 127


def run_capture(cmd: List[str] | str, cwd: Optional[str] = None, env: Optional[Mapping[str, str]] = None, shell: bool = False) -> tuple[int, str]:
    """Run a subprocess and capture combined stdout/stderr and return code.

    Does not stream output to console.
    """
    try:
        proc = subprocess.run(
            cmd if isinstance(cmd, list) else cmd,
            cwd=cwd,
            env=env,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        return proc.returncode or 0, proc.stdout or ""
    except FileNotFoundError:
        return 127, ""


def which(executable: str) -> Optional[str]:
    paths = os.environ.get("PATH", "").split(os.pathsep)
    exts = [""]
    if os.name == "nt":
        pathext = os.environ.get("PATHEXT", ".EXE;.BAT;.CMD").split(";")
        exts = [ext.lower() for ext in pathext]
    for p in paths:
        candidate = os.path.join(p, executable)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
        if os.name == "nt":
            for ext in exts:
                candidate_ext = candidate + ext
                if os.path.isfile(candidate_ext) and os.access(candidate_ext, os.X_OK):
                    return candidate_ext
    return None


def is_windows() -> bool:
    return os.name == "nt"


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)
