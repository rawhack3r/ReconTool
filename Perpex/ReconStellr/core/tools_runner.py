import subprocess, time
from pathlib import Path
from core.log_utils import log_event
from configs.tools_yaml_loader import load_tools
from core.phases import PHASES

def run_tools(target, mode, output_dir, resume_state=None, retry_only=None):
    tools = load_tools()
    results = {}
    errors = []
    stats = []

    subdomain_outputs = []

    for tool in tools:
        name, phase = tool["name"], tool["phase"]
        if retry_only and name not in retry_only: continue
        if resume_state and name in resume_state.get("completed", []): continue

        try:
            begin_time = time.time()
            cmd = tool['command'].format(target=target, output_dir=output_dir)
            out_path = tool.get("output", "").format(target=target, output_dir=output_dir)

            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            duration = round(time.time() - begin_time, 2)

            count = ""
            if proc.returncode == 0:
                if out_path:
                    with open(out_path, "wb") as f:
                        f.write(out)
                    # For subdomain tools, count lines.
                    if phase == "Subdomain Enumeration":
                        n = len(out.decode().splitlines())
                        subdomain_outputs.append(out_path)
                        count = f"[cyan]{n} subdomains[/cyan]"
                results[name] = "completed"
            else:
                raise Exception(err.decode())
            stats.append((phase, name, results[name], count or "-"))
        except Exception as e:
            results[name] = "failed"
            log_event(str(e), output_dir / "error.log")
            errors.append({"tool": name, "error": str(e)})
            stats.append((phase, name, "failed", "-"))

    # (Optional) Merge all subdomain outputs into one here
    if subdomain_outputs:
        unified = Path(output_dir)/"all_subdomains.txt"
        seen = set()
        for f in subdomain_outputs:
            with open(f) as infile:
                for line in infile:
                    line = line.strip()
                    if line and line not in seen:
                        seen.add(line)
        with open(unified, "w") as out:
            for line in sorted(seen):
                out.write(line+"\n")
        # Show summary on CLI if desired

    return results, errors, stats
