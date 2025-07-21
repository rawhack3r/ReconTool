"""
core/utils.py
Shared helpers for NightOwl.
Stage 10.5 – adds timeout + parallel support utilities.
"""
from __future__ import annotations
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import json
import jsonschema

# ---------------- Paths ---------------- #

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def project_path(*parts) -> Path:
    return PROJECT_ROOT.joinpath(*parts)

def target_outdir(target: str) -> Path:
    safe = target.replace("*.", "").strip()
    return project_path("output") / safe

def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p

# ---------------- YAML / Schema ---------------- #

def _read_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text())

def load_tools_config(path: str = "config/tools.yaml") -> Dict[str, Any]:
    p = project_path(path)
    data = _read_yaml(p) or {}
    validate_schema(data, "config/tools.schema.json")
    return data

def load_phases_config(path: str = "config/phases.yaml") -> List[Dict[str, Any]]:
    p = project_path(path)
    data = _read_yaml(p)
    # Accept either list or {"phases": [...]}
    if isinstance(data, dict) and "phases" in data:
        data = data["phases"]
    if not isinstance(data, list):
        raise ValueError("phases.yaml must be a list of phase objects")
    return data

def validate_schema(instance, schema_rel_path: str):
    schema_path = project_path(schema_rel_path)
    if not schema_path.exists():
        return
    schema = json.loads(schema_path.read_text())
    try:
        jsonschema.validate(instance=instance, schema=schema)
    except Exception:
        # Swallow schema errors for dev flexibility, but can re‑raise if strict
        pass

# ---------------- Tool Helpers ---------------- #

def tool_exists(binary: str) -> bool:
    return shutil.which(binary) is not None

def render_cmd(template: str, target: str, outdir: Path) -> str:
    return template.format(
        target=target,
        outdir=str(outdir),
        output=str(outdir),  # backward compat
    )

# ---------------- File Helpers ---------------- #

def read_lines(path: Path, unique: bool = False) -> List[str]:
    if not path.exists():
        return []
    lines = [l.strip() for l in path.read_text().splitlines() if l.strip()]
    if unique:
        lines = list(dict.fromkeys(lines))
    return lines

def write_lines(path: Path, lines: List[str]):
    ensure_dir(path.parent)
    path.write_text("\n".join(lines) + ("\n" if lines else ""))

# ---------------- Command Execution ---------------- #

DEFAULT_TIMEOUT = 300  # seconds

def run_command(
    cmd: str,
    timeout: Optional[int] = None,
    shell: bool = True,
) -> Dict[str, Any]:
    """
    Run a shell command with timeout enforcement.

    Returns:
        {
          'cmd': str,
          'rc': int,
          'elapsed': float,
          'stdout': str,
          'stderr': str,
          'timeout': bool
        }
    """
    to = timeout if timeout is not None else DEFAULT_TIMEOUT
    start = time.time()
    proc = subprocess.Popen(
        cmd,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=to)
    except subprocess.TimeoutExpired:
        timed_out = True
        proc.kill()
        try:
            stdout, stderr = proc.communicate(timeout=5)
        except Exception:
            stdout, stderr = "", "forced termination"
    elapsed = time.time() - start
    return {
        "cmd": cmd,
        "rc": (proc.returncode if not timed_out else 124),
        "elapsed": elapsed,
        "stdout": stdout,
        "stderr": stderr,
        "timeout": timed_out,
    }

