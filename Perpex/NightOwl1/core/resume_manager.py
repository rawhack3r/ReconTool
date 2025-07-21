import json
from pathlib import Path
from core.constants import STATE_FILE

def get_state_file(target):
    return Path("outputs") / target / STATE_FILE

def save_state(state, target):
    with open(get_state_file(target), 'w') as f:
        json.dump(state, f)

def check_resume(target):
    path = get_state_file(target)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None
