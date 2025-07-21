"""
error_handler.py
Persistent scan state + error recording for resume support.
"""
from __future__ import annotations
import datetime as dt
from pathlib import Path
from typing import Dict, Any, List
from core.utils import ensure_dir, write_json, read_json, project_path, target_slug

STATE_VERSION = 1

def state_path_for(target: str) -> Path:
    return project_path("output") / target_slug(target) / "meta" / "scan_state.json"

def load_state(target: str) -> Dict[str, Any]:
    return read_json(state_path_for(target), default={})

def save_state(target: str, state: Dict[str, Any]) -> None:
    state["_version"] = STATE_VERSION
    state["updated"] = dt.datetime.utcnow().isoformat() + "Z"
    write_json(state_path_for(target), state)

def record_phase_complete(target: str, phase: str, state: Dict[str, Any]) -> None:
    done = state.setdefault("completed_phases", [])
    if phase not in done:
        done.append(phase)
    save_state(target, state)

def record_failure(target: str, tool: str, phase: str, error: str, state: Dict[str, Any]) -> None:
    failed = state.setdefault("failed_tools", {})
    failed[tool] = {"phase": phase, "error": error}
    save_state(target, state)

def reset_failures(target: str, state: Dict[str, Any]) -> None:
    state["failed_tools"] = {}
    save_state(target, state)
