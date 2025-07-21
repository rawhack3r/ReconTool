import os
import json
from datetime import datetime

class StateManager:
    @staticmethod
    def save_state(target, state_data):
        state_dir = "state"
        os.makedirs(state_dir, exist_ok=True)
        state_file = os.path.join(state_dir, f"{target}.json")
        
        state_data['last_saved'] = datetime.now().isoformat()
        
        with open(state_file, "w") as f:
            json.dump(state_data, f, indent=2)
    
    @staticmethod
    def load_state(target):
        state_file = os.path.join("state", f"{target}.json")
        if not os.path.exists(state_file):
            return None
        
        try:
            with open(state_file, "r") as f:
                return json.load(f)
        except:
            return None