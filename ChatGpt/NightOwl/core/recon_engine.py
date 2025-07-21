"""
core/recon_engine.py
NightOwl Orchestrator – Stage 10.5
Adds:
 - per-tool timeout
 - passive group parallelization
 - resilient error capture
"""
from __future__ import annotations
import importlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.utils import (
    load_tools_config,
    load_phases_config,
    project_path,
    target_outdir,
    ensure_dir,
    render_cmd,
    tool_exists,
    run_command,
)
from core import error_handler


class ReconTool:
    def __init__(
        self,
        target: str,
        scan_level: str = "light",
        tools: Optional[List[str]] = None,
        phases: Optional[List[str]] = None,
        resume: bool = False,
        ui=None,
        passive_workers: int = 5,
        default_tool_timeout: int = 300,
    ):
        self.target = target
        self.scan_level = scan_level
        self.tools_override = tools
        self.phases_override = phases
        self.resume = resume
        self.ui = ui
        self.passive_workers = passive_workers
        self.default_tool_timeout = default_tool_timeout

        self.tools_cfg = load_tools_config()
        self.phases_cfg = load_phases_config()

        self.outdir = target_outdir(target)
        ensure_dir(self.outdir)

        self.state = error_handler.load_state(target) if resume else {}
        self.completed = set(self.state.get("completed_phases", []))

        if self.ui:
            self.ui.log(f"Output dir: {self.outdir}")

    # ---------------- Main Loop ---------------- #

    def run(self):
        for phase in self.phases_cfg:
            name = phase["name"]

            if self.resume and name in self.completed:
                self._log(f"Skipping {name} (already completed).", style="success")
                continue
            if self.phases_override and name not in self.phases_override:
                continue

            self._phase_start(name)

            phase_tool_names = self._phase_tool_selection(phase)

            # Run grouped passive tools in parallel
            tool_results = {}
            passive_group = [
                t for t in phase_tool_names
                if self.tools_cfg.get(t, {}).get("group") == "passive"
            ]
            serial_tools = [t for t in phase_tool_names if t not in passive_group]

            if passive_group:
                self._log(f"Parallel passive tools: {', '.join(passive_group)}")
                tool_results.update(self._run_parallel(passive_group, phase=name))

            for tname in serial_tools:
                tool_results[tname] = self._run_tool(tname, phase=name)

            # Phase post-processing module
            self._run_phase_module(name, tool_results)

            # Mark completion
            self.completed.add(name)
            self.state["completed_phases"] = list(self.completed)
            error_handler.save_state(self.target, self.state)

            self._phase_end(name)

    # ---------------- Phase Helpers ---------------- #

    def _phase_start(self, name: str):
        if self.ui:
            self.ui.phase_start(name)
        else:
            self._log(f"---- Phase: {name} ----")

    def _phase_end(self, name: str):
        if self.ui:
            self.ui.phase_end(name)
        else:
            self._log(f"Completed phase {name}", style="success")

    def _phase_tool_selection(self, phase_obj: Dict[str, Any]) -> List[str]:
        names = phase_obj.get("tools", [])
        if self.tools_override:
            names = [n for n in names if n in self.tools_override]
        if self.scan_level != "custom":
            names = [
                n for n in names
                if self._tool_meets_scan_level(self.tools_cfg.get(n, {}))
            ]
        return names

    def _tool_meets_scan_level(self, cfg: Dict[str, Any]) -> bool:
        stage = cfg.get("stage", "any")
        if self.scan_level == "light":
            return stage in ("light", "any")
        if self.scan_level == "deep":
            return stage in ("light", "deep", "any")
        if self.scan_level == "deeper":
            return stage in ("light", "deep", "deeper", "any")
        if self.scan_level == "custom":
            return True
        return True

    # ---------------- Tool Execution ---------------- #

    def _run_parallel(self, tool_names: List[str], phase: str) -> Dict[str, Dict[str, Any]]:
        results = {}
        with ThreadPoolExecutor(max_workers=self.passive_workers) as pool:
            future_map = {
                pool.submit(self._run_tool, tname, phase): tname for tname in tool_names
            }
            for future in as_completed(future_map):
                tname = future_map[future]
                try:
                    results[tname] = future.result()
                except Exception as e:
                    self._log(f"{tname} crashed in parallel: {e}", style="error")
                    error_handler.record_failure(self.target, tname, phase, str(e), self.state)
        return results

    def _run_tool(self, tool_name: str, phase: str) -> Dict[str, Any]:
        cfg = self.tools_cfg.get(tool_name)
        if not cfg:
            msg = "Not defined in tools.yaml"
            self._log(f"{tool_name}: {msg}", style="error")
            error_handler.record_failure(self.target, tool_name, phase, msg, self.state)
            return {"tool": tool_name, "status": "undefined"}

        binary = cfg["cmd"].split()[0]
        if not tool_exists(binary):
            msg = f"binary '{binary}' missing in PATH"
            self._log(f"{tool_name}: {msg}", style="warn")
            error_handler.record_failure(self.target, tool_name, phase, msg, self.state)
            return {"tool": tool_name, "status": "missing"}

        cmd = render_cmd(cfg["cmd"], self.target, self.outdir)
        timeout = cfg.get("timeout", self.default_tool_timeout)

        self._log(f"Running {tool_name}: {cmd}")
        result = run_command(cmd, timeout=timeout)
        result["tool"] = tool_name
        result["phase"] = phase
        result["timeout_set"] = timeout

        if result["timeout"]:
            status = f"timeout ({timeout}s)"
            self._log(f"{tool_name} {status}", style="error")
            error_handler.record_failure(self.target, tool_name, phase, status, self.state)
            result["status"] = "timeout"
        elif result["rc"] != 0:
            self._log(f"{tool_name} failed rc={result['rc']}", style="error")
            error_handler.record_failure(self.target, tool_name, phase, result["stderr"], self.state)
            result["status"] = "error"
        else:
            self._log(f"{tool_name} completed in {result['elapsed']:.2f}s", style="success")
            result["status"] = "ok"

        return result

    # ---------------- Phase Module ---------------- #

    def _run_phase_module(self, phase_name: str, tool_results: Dict[str, Any]):
        mod_name = f"phases.{phase_name}"
        try:
            mod = importlib.import_module(mod_name)
        except ImportError:
            self._log(f"No module for phase '{phase_name}' (optional).", style="warn")
            return
        try:
            mod.run(
                target=self.target,
                outdir=self.outdir,
                tool_cfg=self.tools_cfg,
                ui=self.ui,
                scan_level=self.scan_level,
                tool_results=tool_results,
            )
        except Exception as e:
            self._log(f"Phase module {phase_name} crashed: {e}", style="error")
            error_handler.record_failure(self.target, f"__phase__{phase_name}", phase_name, str(e), self.state)

    # ---------------- Logging ---------------- #

    def _log(self, msg: str, style: str = "info"):
        if self.ui:
            # UI handles style codes
            if style == "error":
                self.ui.log_error(msg)
            elif style == "warn":
                self.ui.log_warn(msg)
            elif style == "success":
                self.ui.log_success(msg)
            else:
                self.ui.log(msg)
        else:
            print(f"[{style.upper()}] {msg}")

