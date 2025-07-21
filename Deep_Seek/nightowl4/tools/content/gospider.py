from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_gospider(target, output_dir, state, verbose=False):
    if not state.get("live_urls"):
        return []
    
    input_file = f"{output_dir}/live_hosts/urls.txt"
    with open(input_file, "w") as f:
        f.write("\n".join(state["live_urls"]))
    
    output_file = f"{output_dir}/content/gospider.txt"
    cmd = f"gospider -S {input_file} -o {output_file} -t 50"
    return utils.run_command(cmd, verbose=verbose, output_file=output_file)