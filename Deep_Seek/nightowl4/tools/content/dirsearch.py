from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_dirsearch(target, output_dir, state, verbose=False):
    if not state.get("live_urls"):
        return []
    
    input_file = f"{output_dir}/live_hosts/urls.txt"
    with open(input_file, "w") as f:
        f.write("\n".join(state["live_urls"]))
    
    output_file = f"{output_dir}/content/dirsearch.txt"
    cmd = f"dirsearch -l {input_file} --format=plain -o {output_file}"
    return utils.run_command(cmd, verbose=verbose, output_file=output_file)