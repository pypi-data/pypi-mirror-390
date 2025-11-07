"""Validación básica para pypackage.json"""

import json
from pathlib import Path
from typing import Dict, Any
from rich.console import Console

console = Console()

def validate_pypackage(data: Dict[str, Any]) -> bool:
    """Validación básica de la estructura de pypackage.json"""
    required_fields = ["name", "version", "type"]
    allowed_fields = {
        "type", "name", "version", "description", "authors", "license",
        "dependencies", "devDependencies", "optionalDependencies", "scripts",
        "cli", "pyproject", "useGlobalDeps", "pyprojectUse", "executable",
        "autoResolveConflicts", "autoResolveStrategy",
        "publishRepo", "publishEnvFile"
    }
    
    for field in required_fields:
        if field not in data:
            console.print(f"[red]Error: Missing required field '{field}' in pypackage.json")
            return False
    
    # Validar tipo de proyecto
    if data["type"] not in ["app", "module"]:
        console.print("[red]Error: Project type must be 'app' or 'module'")
        return False
    
    # Validar formato de versión básico
    version = data.get("version", "")
    if version and not all(c.isdigit() or c == '.' for c in version.replace(' ', '')):
        console.print("[yellow]Warning: Version format may be invalid")
    
    # Validar estructura de dependencias
    dependencies = data.get("dependencies", {})
    if not isinstance(dependencies, dict):
        console.print("[red]Error: Dependencies must be a dictionary")
        return False

    dev_deps = data.get("devDependencies", {})
    if dev_deps and not isinstance(dev_deps, dict):
        console.print("[red]Error: devDependencies must be a dictionary")
        return False

    # Advertir sobre campos desconocidos sin fallar
    unknown = [k for k in data.keys() if k not in allowed_fields]
    if unknown:
        console.print(f"[yellow]Warning: Unknown field(s) in pypackage.json will be ignored: {', '.join(unknown)}")

    return True

def safe_load_pypackage(path: Path) -> Dict[str, Any]:
    """Cargar pypackage.json con validación básica"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if validate_pypackage(data):
            return data
        else:
            raise ValueError("Invalid pypackage.json structure")
            
    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid JSON in pypackage.json: {e}")
        raise
    except Exception as e:
        console.print(f"[red]Error loading pypackage.json: {e}")
        raise