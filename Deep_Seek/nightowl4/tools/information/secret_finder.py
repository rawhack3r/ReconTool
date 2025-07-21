from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_secret_finder(target, output_dir, state, verbose=False):
    if not state.get("live_urls"):
        return []
    
    content = "\n".join(state["live_urls"])
    return utils.extract_secrets(content)