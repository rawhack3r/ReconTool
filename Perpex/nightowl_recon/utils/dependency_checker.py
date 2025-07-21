import shutil, subprocess

def check_dependencies():
    tools=["amass","subfinder","nuclei","naabu","httpx"]
    out={}
    for t in tools:
        p=shutil.which(t)
        if not p: out[t]={"available":False,"error":"not found"}
        else:
            try: v=subprocess.check_output([t,"-version"],stderr=subprocess.STDOUT).decode().splitlines()[0]
            except: v="unknown"
            out[t]={"available":True,"version":v}
    return out
