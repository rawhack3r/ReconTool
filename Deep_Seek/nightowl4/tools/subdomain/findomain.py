from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_findomain(target, output_dir, verbose=False):
    output_file = f"{output_dir}/subdomains/findomain.txt"
    cmd = f"findomain -t {target} -o"
    result = utils.run_command(cmd, verbose=verbose)
    if result:
        with open(output_file, "w") as f:
            f.write(result)
        return result.splitlines()
    return []