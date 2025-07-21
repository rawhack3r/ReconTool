from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_email_extractor(target, output_dir, state, verbose=False):
    if not state.get("live_urls"):
        return []
    
    content = "\n".join(state["live_urls"])
    return utils.extract_emails(content)