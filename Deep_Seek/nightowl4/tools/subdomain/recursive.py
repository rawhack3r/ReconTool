from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_recursive_enum(target, output_dir, state, verbose=False):
    if not state.get("subdomains"):
        return []
    
    candidate_domains = [d for d in state["subdomains"] if d.count('.') < 4]
    new_subdomains = []
    
    for domain in candidate_domains:
        if len(domain) > 30 or not any(kw in domain for kw in ["dev", "staging", "test"]):
            continue
            
        cmd = f"subfinder -d {domain} -silent"
        result = utils.run_command(cmd, verbose=verbose)
        if result:
            new_subdomains.extend(result.splitlines())
    
    return new_subdomains