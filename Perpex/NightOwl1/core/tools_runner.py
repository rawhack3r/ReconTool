from core.plugin_loader import load_tools_from_yaml
from typing import Dict, List, Any
from pathlib import Path


def run_tools(target: str, mode: str, output_dir: Path, resume_state=None, retry_only=None):
    tools = load_tools_from_yaml()
    results = {}
    stats: List[tuple] = []
    errors: List[Dict[str, Any]] = []
    subdomain_outputs = []

    for tool in tools:
        if retry_only and tool.name not in retry_only:
            continue
        if resume_state and tool.name in resume_state.get("completed", []):
            continue

        success, path, duration, err = tool.run(target, output_dir)

        count = "-"
        if tool.phase == "Subdomain Enumeration" and path:
            lines = path.read_text().splitlines()
            count = str(len(lines))
            subdomain_outputs.append(path)

        results[tool.name] = "completed" if success else "failed"
        stats.append((tool.phase, tool.name, results[tool.name], count))

        if err:
            errors.append({"tool": tool.name, "error": err})

    # Create unified subdomain list
    if subdomain_outputs:
        unified = output_dir / "all_subdomains.txt"
        all_subs = set()
        for f in subdomain_outputs:
            all_subs.update(line.strip() for line in f.read_text().splitlines() if line.strip())
        unified.write_text("\n".join(sorted(all_subs)))

    return results, errors, stats
