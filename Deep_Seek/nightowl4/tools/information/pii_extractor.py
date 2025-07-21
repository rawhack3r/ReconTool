from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_pii_extractor(target, output_dir, state, verbose=False):
    if not state.get("live_urls"):
        return []
    
    content = "\n".join(state["live_urls"])
    emails = utils.extract_emails(content)
    phones = utils.extract_phones(content)
    names = utils.extract_names(content)
    return emails + phones + names