from core.utils import Utils

def run(content):
    emails = Utils.extract_emails(content)
    phones = Utils.extract_phones(content)
    names = Utils.extract_names(content)
    return emails + phones + names