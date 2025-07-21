from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_bucket_finder(target, output_dir, state, verbose=False):
    if not state.get("subdomains"):
        return []
    
    return utils.find_buckets(state["subdomains"])