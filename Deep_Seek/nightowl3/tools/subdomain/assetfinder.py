import subprocess

def run(target, output_dir):
    cmd = f"assetfinder -subs-only {target}"
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=600
        )
        if result.returncode == 0:
            subdomains = result.stdout.splitlines()
            # Save to file
            with open(f"{output_dir}/assetfinder.txt", "w") as f:
                f.write("\n".join(subdomains))
            return subdomains
        return []
    except:
        return []