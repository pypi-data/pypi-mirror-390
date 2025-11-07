from __future__ import annotations

import os
import sys
import json
from pathlib import Path
from typing import Iterable, Optional, Dict, Tuple, List
import tempfile
import hashlib
import platform
import subprocess
import re
from rich.console import Console
from rich.prompt import Prompt, Confirm
from .utils import run, run_capture, is_windows, ensure_dir, VERBOSE
from .config import PyPackage

console = Console()


DEF_VENV_DIR = ".venv"

# Global dependencies override (None means use project setting)
GLOBAL_DEPS_OVERRIDE: Optional[bool] = None


def set_global_deps_override(flag: Optional[bool]) -> None:
    global GLOBAL_DEPS_OVERRIDE
    GLOBAL_DEPS_OVERRIDE = flag


def _use_global_deps(cwd: Optional[str]) -> bool:
    if GLOBAL_DEPS_OVERRIDE is not None:
        return bool(GLOBAL_DEPS_OVERRIDE)
    try:
        pkg = PyPackage.load(cwd)
        return bool(getattr(pkg, "useGlobalDeps", False))
    except Exception:
        return False


def venv_dir(cwd: Optional[str] = None) -> Path:
    return Path(cwd or os.getcwd()) / DEF_VENV_DIR


def venv_python(cwd: Optional[str] = None) -> Path:
    vdir = venv_dir(cwd)
    if is_windows():
        return vdir / "Scripts" / "python.exe"
    return vdir / "bin" / "python"


def venv_exists(cwd: Optional[str] = None) -> bool:
    """Check if a virtual environment exists in the specified directory.
    
    Args:
        cwd: Directory to check for virtual environment (default: current directory)
        
    Returns:
        bool: True if a virtual environment exists, False otherwise
    """
    vdir = venv_dir(cwd)
    if not vdir.exists():
        return False
        
    # Check for the Python executable in the venv
    python_exe = vdir / ("Scripts" if is_windows() else "bin") / ("python.exe" if is_windows() else "python")
    return python_exe.exists()


def _confirm_yn(prompt: str, default: bool = True) -> bool:
    """Ask for confirmation with y/n input.
    
    Args:
        prompt: The prompt to display
        default: The default value if user just presses Enter
        
    Returns:
        bool: True if user answered 'y' or 'Y', False if 'n' or 'N'
    """
    from rich.prompt import Prompt
    
    while True:
        response = Prompt.ask(prompt, default="Y" if default else "N")
        response = response.strip().lower()
        if not response:  # User pressed Enter
            return default
        if response in ('y', 'yes'):
            return True
        if response in ('n', 'no'):
            return False
        console.print("[yellow]Please enter 'y' or 'n'[/]")


def ensure_venv(cwd: Optional[str] = None, python: Optional[str] = None, interactive: bool = False) -> Optional[Path]:
    """Ensure virtual environment exists. Returns path to venv Python or None if user declines."""
    # If project is configured to use global dependencies, return system python
    if _use_global_deps(cwd):
        return Path(sys.executable)
        
    vdir = venv_dir(cwd)
    if not vdir.exists():
        if not interactive:
            console.print(f"[cyan]Creating virtual environment at {vdir}...")
            # For Python 3.11+, we don't need --with-pip as pip is included by default
            cmd = [python or sys.executable, "-m", "venv", str(vdir)]
            code = run(cmd)
            if code != 0:
                raise RuntimeError("Failed to create virtual environment")
            
            # Ensure pip is properly installed and up-to-date
            python_exe = venv_python(cwd)
            ensure_pip_cmd = [str(python_exe), "-m", "ensurepip", "--upgrade"]
            pip_cmd = [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"]
            
            # First ensure pip is installed
            ensure_code = run(ensure_pip_cmd, cwd=cwd)
            if ensure_code != 0:
                console.print("[yellow]Warning: Failed to ensure pip is installed in the virtual environment")
                return python_exe
                
            # Then upgrade pip
            pip_code = run(pip_cmd, cwd=cwd)
            if pip_code != 0:
                console.print("[yellow]Warning: Failed to upgrade pip in the virtual environment")
                
            return python_exe
        else:
            # Preguntar al usuario si quiere crear el venv
            if not _confirm_yn(f"[yellow]No virtual environment found at {vdir}. Do you want to create one?", default=True):
                console.print("[yellow]Using system Python (no virtual environment).")
                return None
                
            console.print(f"[cyan]Creating virtual environment at {vdir}...")
            cmd = [python or sys.executable, "-m", "venv", str(vdir)]
            code = run(cmd)
            if code != 0:
                raise RuntimeError("Failed to create virtual environment")
            
            # Ensure pip is properly installed and up-to-date for interactive mode too
            python_exe = venv_python(cwd)
            ensure_pip_cmd = [str(python_exe), "-m", "ensurepip", "--upgrade"]
            pip_cmd = [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"]
            
            # First ensure pip is installed
            ensure_code = run(ensure_pip_cmd, cwd=cwd)
            if ensure_code != 0:
                console.print("[yellow]Warning: Failed to ensure pip is installed in the virtual environment")
                return python_exe
                
            # Then upgrade pip
            pip_code = run(pip_cmd, cwd=cwd)
            if pip_code != 0:
                console.print("[yellow]Warning: Failed to upgrade pip in the virtual environment")
                
            return python_exe
    
    return venv_python(cwd)


def _pretty_pip_line(line: str) -> tuple[str, str | None]:
    """Return (text, style) for a pip output line."""
    s = line.strip()
    lower = s.lower()
    if not s:
        return ("", None)
    if "error" in lower or "failed" in lower:
        return (s, "red")
    if "warning" in lower:
        return (s, "yellow")
    if s.startswith("Successfully ") or "successfully installed" in lower or "successfully uninstalled" in lower:
        return (s, "green")
    if "requirement already satisfied" in lower:
        return (s, "dim")
    if s.startswith("Collecting ") or s.startswith("Downloading ") or s.startswith("Building wheel"):
        return (s, "cyan")
    if s.startswith("Uninstalling "):
        return (s, "cyan")
    return (s, None)


def _merge_constraints(constraints_list: List[str]) -> str:
    """Normalize and merge multiple constraint strings into a single, valid spec.

    - Replaces ' and ' with ','
    - Removes spaces
    - Splits by ',' and cleans tokens
    - Repairs accidental splits like '>=7.4.' + '2' into '>=7.4.2'
    - Drops empty/invalid tokens
    """
    # Join and normalize separators
    raw = ",".join(constraints_list)
    raw = raw.replace(" and ", ",").replace(" ", "")
    # Tokenize by comma
    toks = [t for t in raw.split(",") if t]
    # Repair tokens where a trailing '.' was split from the next numeric piece
    repaired: List[str] = []
    i = 0
    while i < len(toks):
        t = toks[i]
        if t.endswith(".") and i + 1 < len(toks) and toks[i+1].isdigit():
            t = t + toks[i+1]
            i += 2
        else:
            i += 1
        repaired.append(t)
    # Validate basic operator prefix
    valid_ops = ("==", ">=", "<=", ">", "<", "~=", "!=")
    cleaned: List[str] = []
    for t in repaired:
        if not t:
            continue
        # Remove accidental duplicate dots at end
        while t.endswith(".."):
            t = t[:-1]
        if t.endswith(".") and any(t.startswith(op) for op in valid_ops):
            # likely truncated, skip
            continue
        if any(t.startswith(op) for op in valid_ops):
            cleaned.append(t)
    # De-duplicate while preserving order
    seen = set()
    result = []
    for t in cleaned:
        if t not in seen:
            seen.add(t)
            result.append(t)
    return ",".join(result)


def pip(cmd_args: list[str], cwd: Optional[str] = None) -> int:
    """Run pip as a subprocess and pretty-print its output."""
    cmd = [sys.executable, "-m", "pip", *cmd_args]
    try:
        with console.status("[cyan]Working..."):
            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            assert proc.stdout is not None
            satisfied: list[str] = []
            conflicts: list[tuple[str, str, str]] = []  # (requiring, requirement_spec, installed)
            suppress_next_path_hint = False
            for raw in proc.stdout:
                line = raw.rstrip("\n")
                # Skip noisy/verbose lines
                if not line.strip():
                    continue
                # Hide INFO chatter
                if line.startswith("INFO:") and not VERBOSE:
                    continue
                if line.startswith("Looking in links:"):
                    continue
                if line.startswith("Requirement already satisfied:"):
                    # Extract package name before ' in '
                    try:
                        pkg = line.split(":", 1)[1].strip().split(" in ", 1)[0]
                        satisfied.append(pkg)
                    except Exception:
                        satisfied.append(line)
                    continue
                # Hide PATH not on PATH warnings (two-line block) unless verbose
                if not VERBOSE and ("which is not on PATH." in line or line.strip().startswith("Consider adding this directory to PATH")):
                    # skip both the warning and the hint line
                    suppress_next_path_hint = True
                    continue
                if suppress_next_path_hint:
                    suppress_next_path_hint = False
                    continue

                # Hide cache/download/build/install chatter unless verbose
                if not VERBOSE:
                    if (
                        line.startswith("Collecting ")
                        or line.startswith("Downloading ")
                        or line.startswith("Building wheel")
                        or line.startswith("Installing collected packages:")
                        or line.startswith("Successfully downloaded")
                        or line.startswith("Successfully built")
                        or line.startswith("Preparing metadata")
                        or line.startswith("Using cached ")
                        or line.startswith("Processing ")
                        or line.startswith("Saved ")
                        or "File was already downloaded" in line
                    ):
                        continue
                    if line.startswith("Successfully installed"):
                        # Hide verbose success; we'll print a final Done
                        continue

                # Capture resolver conflict notes
                if line.startswith("ERROR: pip's dependency resolver"):
                    # We'll summarize; don't print the generic paragraph
                    continue
                mconf = re.match(r"^(?P<reqpkg>\S+)\s+(?P<reqver>\S+)\s+requires\s+(?P<dep>\S+)\s*(?P<constraints>.*?),\s+but you have\s+(?P<dep2>\S+)\s+(?P<havever>\S+)", line)
                if mconf:
                    requiring = f"{mconf.group('reqpkg')} {mconf.group('reqver')}"
                    dep_name = mconf.group('dep')
                    constraints_raw = (mconf.group('constraints') or "").strip()
                    spec = f"{dep_name} {constraints_raw}".strip()
                    installed = f"{mconf.group('dep2')} {mconf.group('havever')}"
                    conflicts.append((requiring, spec, installed))
                    continue

                # Pretty print remaining lines
                text, style = _pretty_pip_line(line)
                if style:
                    console.print(text, style=style)
                else:
                    console.print(text)
            proc.wait()
        # Print aggregated satisfied summary
        if satisfied:
            shown = satisfied[:6]
            more = len(satisfied) - len(shown)
            summary = ", ".join(shown)
            if more > 0:
                summary += f" (+{more} more)"
            console.print(f"[dim]Already satisfied: {summary}")
        # Summarize conflicts, if any
        if conflicts:
            console.print("[red]Dependency conflicts detected:[/]")
            for requiring, spec, installed in conflicts[:6]:
                console.print(f" - {requiring} requires {spec}, but installed {installed}")
            if len(conflicts) > 6:
                console.print(f"  (+{len(conflicts)-6} more)")
            console.print("[yellow]Tips:[/]")
            console.print(" - Try: pydep add --upgrade <requiring-package>")
            console.print(" - Or pin a compatible version: pydep add '<dep><constraint>'")
            # Build proposed constraints map dep -> merged constraint string
            cons_map: dict[str, list[str]] = {}
            for _requiring, spec, _installed in conflicts:
                # spec like 'starlette <0.50.0 and >=0.40.0' or 'qrcode <8.0.0,>=7.4.2'
                parts = spec.split(maxsplit=1)
                if not parts:
                    continue
                dep = parts[0]
                rest = parts[1] if len(parts) > 1 else ""
                if rest:
                    cons_map.setdefault(dep, []).append(rest)
            if cons_map:
                # Load project settings to decide auto behavior
                try:
                    pkg_cfg = PyPackage.load(cwd)
                except Exception:
                    pkg_cfg = None
                auto_mode = bool(getattr(pkg_cfg, "autoResolveConflicts", False))
                strategy = getattr(pkg_cfg, "autoResolveStrategy", "constraints") or "constraints"

                console.print("\n[bold]Resolution options:[/]")
                for dep, lst in cons_map.items():
                    console.print(f" - {dep}: " + "; ".join(lst))
                if auto_mode:
                    console.print("[cyan]Auto-resolve is enabled in project config. Applying constraints automatically...")
                    choice = "1"
                else:
                    console.print("\n  1) Apply constraints automatically (recommended)")
                    console.print("  2) Specify versions manually")
                    console.print("  3) Skip")
                    choice = Prompt.ask("Choose", choices=["1","2","3"], default="1")
                reqs: list[str] = []
                if choice == "1":
                    for dep, lst in cons_map.items():
                        merged = _merge_constraints(lst)
                        reqs.append(f"{dep}{merged}")
                elif choice == "2":
                    console.print("Enter versions (blank to skip a package):")
                    for dep, lst in cons_map.items():
                        hint = "; ".join(lst)
                        ver = Prompt.ask(f"  {dep} version (hint: {hint})", default="")
                        if ver.strip():
                            # Accept raw spec like '==0.49.0' or full constraint string
                            if any(ver.strip().startswith(ch) for ch in ["<", ">", "=", "~", "!"]):
                                reqs.append(f"{dep}{ver.strip()}")
                            else:
                                reqs.append(f"{dep}=={ver.strip()}")
                # choice == 3 => do nothing
                if reqs:
                    console.print("[cyan]Resolving with selected constraints...")
                    rc2 = pip(["install", "--upgrade", *reqs], cwd=cwd)
                    if rc2 == 0:
                        # Persist resolved specs
                        try:
                            pkg = PyPackage.load(cwd)
                        except Exception:
                            pkg = None
                        if pkg is not None:
                            modified = False
                            for r in reqs:
                                # r like 'starlette>=0.40.0,<0.50.0' or 'starlette==0.49.0'
                                dep = r.split("[",1)[0].split("<",1)[0].split(">",1)[0].split("=",1)[0].split("~",1)[0].split("!",1)[0].strip()
                                if strategy == "pin":
                                    ver = get_installed_version(dep)
                                    if ver:
                                        pkg.dependencies[dep] = f"=={ver}"
                                        modified = True
                                else:
                                    spec = r[len(dep):]
                                    pkg.dependencies[dep] = spec if spec else pkg.dependencies.get(dep, "*")
                                    modified = True
                            if modified:
                                pkg.save(cwd)
                                from .installer import generate_lockfile
                                with console.status("[cyan]Regenerating lockfile..."):
                                    generate_lockfile(fast=True, quiet=True)
                        console.print("[green]Resolution succeeded. Running a quick audit summary...")
                        # Quick post-install audit for changed deps
                        try:
                            from .installer import run_module_capture as _rmc  # type: ignore
                        except Exception:
                            _rmc = run_module_capture
                        code_a, out_a = _rmc("pip_audit", args=["--format", "json"], cwd=cwd) if 'run_module_capture' in globals() else (1, "")
                        try:
                            data = json.loads(out_a) if out_a else []
                        except Exception:
                            data = []
                        affected = set(d.split("[",1)[0].strip() for d in reqs)
                        vuln_count = 0
                        if isinstance(data, dict) and isinstance(data.get("dependencies"), list):
                            it = data["dependencies"]
                        elif isinstance(data, list):
                            it = data
                        else:
                            it = []
                        for entry in it:
                            nm = (entry.get("name") or "").lower()
                            if nm in (a.lower() for a in affected):
                                vulns = entry.get("vulns") or []
                                vuln_count += len(vulns)
                        if vuln_count:
                            console.print(f"[yellow]{vuln_count} vulnerability finding(s) reported for updated packages. Consider 'pydep audit' for details.")
                        console.print("[green]Done")
                        return 0
                    else:
                        console.print("[red]Failed to resolve conflicts automatically.")
        console.print("[green]Done")
        return proc.returncode or 0
    except FileNotFoundError:
        console.print("[red]pip not found")
        return 127
    except Exception as e:
        console.print(f"[red]pip error: {e}")
        return 1



def get_installed_version(package: str, cwd: Optional[str] = None) -> Optional[str]:
    """Return installed version for package in the managed venv, or None if not found."""
    py = ensure_venv(cwd)
    code, out = run_capture([str(py), "-m", "pip", "show", package], cwd=cwd)
    if code != 0 or not out:
        return None
    for line in out.splitlines():
        if line.lower().startswith("version:"):
            return line.split(":", 1)[1].strip()
    return None


def global_cache_dir() -> Path:
    """Return path to the global cache directory used by PyDep."""
    home = Path.home()
    base = home / ".pydep" / "cache"
    base.mkdir(parents=True, exist_ok=True)
    return base


import time
import shutil

def cleanup_old_cache(max_age_days: int = 30):
    """Eliminar paquetes del caché más antiguos que max_age_days"""
    cache_dir = global_cache_dir()
    if not cache_dir.exists():
        return
    
    current_time = time.time()
    removed_count = 0
    
    for item in cache_dir.iterdir():
        if item.is_file():
            # Calcular antigüedad del archivo
            file_age = current_time - item.stat().st_mtime
            if file_age > (max_age_days * 24 * 60 * 60):  # Convertir días a segundos
                try:
                    item.unlink()
                    removed_count += 1
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not remove {item}: {e}")
    
    if removed_count > 0:
        console.print(f"[green]Cleaned up {removed_count} old package(s) from cache")

from pip._internal.cli.main import main as pip_main

def pip_download(packages: Iterable[str], dest: Path, cwd: Optional[str] = None) -> int:
    """
    Download distributions for given package requirements into dest (no deps),
    usando la API interna de pip en vez de subprocess.
    """
    cleanup_old_cache()

    args = [
        "download",
        "--no-deps",
        "-d", str(dest),
        *list(packages)
    ]

    try:
        # pip_main devuelve código de salida como int
        return pip_main(args)
    except SystemExit as e:
        # pip a veces hace sys.exit()
        return int(e.code) if isinstance(e.code, int) else 1
    except Exception as e:
        console.print(f"[red]pip internal error: {e}[/]")
        return 1



def compute_hashes_for_package(name: str, version: str, cwd: Optional[str] = None) -> List[str]:
    """Download the package wheel/sdist for exact version and compute sha256 hashes.

    Returns list of strings like 'sha256:<hex>'. For simplicity, we hash the downloaded
    artifact(s) for the current platform.
    """
    req = f"{name}=={version}"
    hashes: List[str] = []
    # Primero intenta usar el caché global para evitar descargas
    cache = global_cache_dir()
    candidates = list(cache.glob(f"{name.replace('-', '_')}*-{version}*.whl")) + list(cache.glob(f"{name}*-{version}*.whl"))
    if candidates:
        for file in candidates:
            if file.is_file():
                h = hashlib.sha256()
                with file.open("rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        h.update(chunk)
                hashes.append(f"sha256:{h.hexdigest()}")
        return hashes

    # Si no está en caché, descarga temporalmente y calcula hash
    with tempfile.TemporaryDirectory() as td:
        tmpdir = Path(td)
        rc = pip_download([req], dest=tmpdir, cwd=cwd)
        if rc != 0:
            return hashes
        for file in tmpdir.iterdir():
            if file.is_file():
                h = hashlib.sha256()
                with file.open("rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        h.update(chunk)
                hashes.append(f"sha256:{h.hexdigest()}")
    return hashes


def freeze_versions(cwd: Optional[str] = None, ensure_venv_exists: bool = True) -> Dict[str, str]:
    """Return mapping name -> exact version from pip freeze in the managed venv.
    
    Args:
        cwd: Working directory (default: current directory)
        ensure_venv_exists: If True, ensure a venv exists before proceeding. If False and no venv exists,
                           return an empty dict.
                           
    Returns:
        Dict mapping package names to their versions
    """
    if ensure_venv_exists or venv_exists(cwd):
        py = ensure_venv(cwd)
        code, out = run_capture([str(py), "-m", "pip", "freeze"], cwd=cwd)
        result: Dict[str, str] = {}
        if code != 0 or not out:
            return result
        for line in out.splitlines():
            line = line.strip()
            if not line or line.startswith("-") or "==" not in line:
                continue
            name, ver = line.split("==", 1)
            result[name.lower()] = ver
        return result
    return {}


def get_global_packages() -> Dict[str, str]:
    """Get a mapping of globally installed packages and their versions.
    
    Returns:
        Dict mapping package names to their versions
    """
    code, out = run_capture([sys.executable, "-m", "pip", "freeze"])
    result: Dict[str, str] = {}
    if code != 0 or not out:
        return result
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("-") or "==" not in line:
            continue
        name, ver = line.split("==", 1)
        result[name.lower()] = ver
    return result


def get_requires(package: str, cwd: Optional[str] = None) -> List[str]:
    """Return list of required package names (lowercased) for the given package using pip show."""
    py = ensure_venv(cwd)
    code, out = run_capture([str(py), "-m", "pip", "show", package], cwd=cwd)
    if code != 0 or not out:
        return []
    for line in out.splitlines():
        if line.startswith("Requires:"):
            reqs = line.split(":", 1)[1].strip()
            if not reqs:
                return []
            # Split by comma and take the name part (strip extras and version if present)
            names = []
            for item in reqs.split(","):
                nm = item.strip()
                if not nm:
                    continue
                # drop extras marker like pkg[extra]
                nm = nm.split("[")[0].strip()
                names.append(nm.lower())
            return names
    return []


def dependency_closure(top_level: List[str], versions: Dict[str, str], cwd: Optional[str] = None) -> List[str]:
    """Compute dependency closure starting from top-level package names, using pip show Requires field.

    Only includes packages present in 'versions'. Returns a list of lowercased names.
    """
    seen: set[str] = set()
    queue: List[str] = [n.lower() for n in top_level]
    while queue:
        name = queue.pop(0)
        if name in seen:
            continue
        if name not in versions:
            # Not installed or not part of this environment
            seen.add(name)
            continue
        seen.add(name)
        for child in get_requires(name, cwd=cwd):
            if child not in seen:
                queue.append(child)
    # Filter to those with versions (installed)
    return [n for n in seen if n in versions]


def pip_list_outdated(cwd: Optional[str] = None) -> List[dict]:
    """Return list of outdated packages using pip list --outdated --format=json."""
    py = ensure_venv(cwd)
    code, out = run_capture([str(py), "-m", "pip", "list", "--outdated", "--format", "json"], cwd=cwd)
    if code != 0 or not out:
        return []
    try:
        data = json.loads(out)
        if isinstance(data, list):
            return data
    except Exception:
        return []
    return []


def pip_show(package: str, cwd: Optional[str] = None) -> Dict[str, str]:
    """Return parsed fields from pip show output as a dict."""
    py = ensure_venv(cwd)
    code, out = run_capture([str(py), "-m", "pip", "show", package], cwd=cwd)
    result: Dict[str, str] = {}
    if code != 0 or not out:
        return result
    for line in out.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            result[k.strip()] = v.strip()
    return result


def generate_lockfile(cwd: Optional[str] = None, fast: bool = False, quiet: bool = False, output_file: Optional[Path] = None) -> Path:
    """Generate a lockfile with exact versions and hashes for project dependencies only.

    We compute the dependency closure starting from pypackage.json dependencies.
    
    Args:
        cwd: Working directory (default: current directory)
        fast: If True, skip computing hashes for faster generation
        quiet: If True, suppress output messages
        output_file: Optional path to the output lockfile. If None, uses pypackage-lock.json in cwd.
    
    Returns:
        Path to the generated lockfile
    """
    versions = freeze_versions(cwd)
    try:
        pkg = PyPackage.load(cwd)
        top = list((pkg.dependencies or {}).keys())
    except Exception:
        top = []
    closure = dependency_closure(top, versions, cwd=cwd) if top else list(versions.keys())
    lock: Dict[str, Dict[str, object]] = {}
    if not quiet:
        console.print("[cyan]Computing hashes for lockfile...")
    for name_lower in sorted(closure):
        ver = versions.get(name_lower)
        if not ver:
            continue
        hashes: List[str] = []
        if not fast:
            hashes = compute_hashes_for_package(name_lower, ver, cwd=cwd)
        lock[name_lower] = {
            "version": f"=={ver}",
            "hashes": hashes,
        }
    meta = {
        "python": platform.python_version(),
        "platform": platform.platform(),
    }
    lock_data = {
        "lockfileVersion": 1,
        "metadata": meta,
        "packages": lock,
    }
    
    # Use the provided output file or default to pypackage-lock.json in cwd
    if output_file is None:
        path = PyPackage.lockfile_path(cwd)
    else:
        path = output_file
    
    # Ensure the parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the lockfile
    path.write_text(json.dumps(lock_data, indent=2), encoding="utf-8")
    
    if not quiet:
        console.print(f"[green]Lockfile written to {path}")
    
    return path


def install_with_cache(packages: Iterable[str], cwd: Optional[str] = None) -> int:
    """Install given package requirements using the global cache to avoid re-downloads.

    Accepts pip options mixed with requirements (e.g., ["--upgrade", "requests"]).
    """
    cache = global_cache_dir()
    args = list(packages)
    opts = [a for a in args if isinstance(a, str) and a.startswith("-")]
    reqs = [a for a in args if not (isinstance(a, str) and a.startswith("-"))]
    # If using global deps, prefer --user installs to avoid admin
    if _use_global_deps(cwd) and "--user" not in opts:
        opts = ["--user", *opts]
    if reqs:
        # Pre-download artifacts for requirements only
        pip_download(reqs, dest=cache, cwd=cwd)
    # Try install from cache first
    base = ["install", *opts, "--no-index", "--find-links", str(cache), *reqs]
    rc = pip(base, cwd=cwd)
    if rc != 0:
        # Fallback to network with cache as find-links
        base = ["install", *opts, "--find-links", str(cache), *reqs]
        rc = pip(base, cwd=cwd)
    return rc


def install_packages(packages: Iterable[str], cwd: Optional[str] = None) -> int:
    if not packages:
        return 0
    # Hide pip options in the display list
    display = [p for p in packages if not (isinstance(p, str) and p.startswith("-"))]
    console.print("[green]Installing packages:", ", ".join(display))
    return install_with_cache(packages, cwd=cwd)


def remove_packages(packages: Iterable[str], cwd: Optional[str] = None) -> int:
    if not packages:
        return 0
    console.print("[yellow]Uninstalling packages:", ", ".join(packages))
    return pip(["uninstall", "-y", *packages], cwd=cwd)


def install_all(cwd: Optional[str] = None, use_global: bool = False) -> int:
    try:
        pkg = PyPackage.load(cwd)
    except FileNotFoundError:
        console.print("[red]pypackage.json not found in the current directory")
        return 1
    
    # Configurar el uso de dependencias globales si se solicita
    if use_global:
        set_global_deps_override(True)
        
    # Si hay lockfile, instalar exactamente desde lockfile
    lock_path = PyPackage.lockfile_path(cwd)
    if lock_path.exists():
        try:
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            packages = [f"{name}{entry.get('version','')}" for name, entry in lock.get("packages", {}).items()]
            if packages:
                console.print("[cyan]Installing from lockfile...")
                return install_with_cache(packages, cwd=cwd)
        except Exception as e:
            console.print(f"[yellow]Invalid lockfile. Ignoring and resolving from pypackage.json. Error: {e}")

    # Instalar dependencias principales
    norm_reqs = _normalize_requirements(pkg.dependencies)
    if norm_reqs:
        console.print("[cyan]Installing main dependencies...")
        code = install_packages(norm_reqs, cwd=cwd)
        if code != 0:
            return code
        console.print("[green]✓ Main dependencies installed")
    else:
        console.print("[yellow]No main dependencies to install.")
        ensure_venv(cwd)
    
    # Instalar dependencias de desarrollo si existen
    if getattr(pkg, 'devDependencies', None):
        dev_reqs = _normalize_requirements(pkg.devDependencies)
        if dev_reqs:
            console.print("[cyan]Installing dev dependencies...")
            code = install_packages(dev_reqs, cwd=cwd)
            if code != 0:
                return code
            console.print("[green]✓ Dev dependencies installed")
    
    # Manejar dependencias opcionales
    if hasattr(pkg, 'optionalDependencies') and pkg.optionalDependencies:
        console.print("\n[bold]Optional dependency groups found:[/]")
        for group, deps in pkg.optionalDependencies.items():
            if not deps:
                continue
                
            if _confirm_yn(f"Install optional '{group}' dependencies? ({len(deps)} packages)", default=False):
                group_reqs = _normalize_requirements(deps)
                if group_reqs:
                    console.print(f"[cyan]Installing {group} dependencies...")
                    code = install_packages(group_reqs, cwd=cwd)
                    if code == 0:
                        console.print(f"[green]✓ {group} dependencies installed")
                    else:
                        console.print(f"[yellow]! Some {group} dependencies failed to install")
    
    return 0

def _normalize_requirements(deps: dict) -> list[str]:
    """Normalize requirements from a dict of {name: spec} to a list of pip-compatible requirements."""
    norm_reqs = []
    for name, spec in deps.items():
        if not spec:
            continue
            
        s = str(spec).strip()
        # Sanitize dangling semicolons and ensure proper marker formatting
        if ";" in s:
            left, sep, right = s.partition(";")
            left = left.strip()
            right = right.strip()
            if not right:
                # Dangling marker separator; drop it
                s = left
            else:
                # Keep environment marker with a space before ';' per PEP 508
                s = f"{left} ; {right}" if left else f" ; {right}"
        if s.startswith("^") and "." in s:
            # Manejar ^x.y.z como >=x.y.z,<x+1.0.0
            base = s[1:]
            parts = base.split(".")
            try:
                major = int(parts[0])
                upper = f"<{major+1}.0.0"
                norm_reqs.append(f"{name}>={base},{upper}")
                continue
            except (ValueError, IndexError):
                pass
        
        # Para cualquier otro caso, incluyendo versiones exactas o rangos complejos
        if any(c in s for c in "=<>~!"):
            norm_reqs.append(f"{name}{s}")
        else:
            norm_reqs.append(f"{name}=={s}")
    
    return norm_reqs


def ensure_tool(package: str, cwd: Optional[str] = None) -> int:
    """Ensure a tool is installed inside the managed venv (e.g., 'build', 'twine', 'pip-audit')."""
    return pip(["install", package], cwd=cwd)


def run_module(module: str, args: list[str] | tuple[str, ...] = (), cwd: Optional[str] = None, force_stream: bool = False) -> int:
    """Run a Python module inside the managed venv (e.g., python -m build)."""
    py = ensure_venv(cwd)
    return run([str(py), "-m", module, *list(args)], cwd=cwd, force_stream=force_stream)


def run_module_capture(module: str, args: list[str] | tuple[str, ...] = (), cwd: Optional[str] = None) -> tuple[int, str]:
    """Run a Python module inside the managed venv and capture its combined output."""
    py = ensure_venv(cwd)
    return run_capture([str(py), "-m", module, *list(args)], cwd=cwd)
