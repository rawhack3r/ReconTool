import os
import json
import zlib
import pickle
from datetime import datetime

class StateManager:
    @staticmethod
    def save_state(target, state_data):
        state_dir = "state"
        os.makedirs(state_dir, exist_ok=True)
        state_file = os.path.join(state_dir, f"{target}.state")
        
        # Add timestamp
        state_data['last_saved'] = datetime.now().isoformat()
        
        # Compress and save
        with open(state_file, "wb") as f:
            f.write(zlib.compress(pickle.dumps(state_data)))
    
    @staticmethod
    def load_state(target):
        state_file = os.path.join("state", f"{target}.state")
        if not os.path.exists(state_file):
            return None
        
        try:
            with open(state_file, "rb") as f:
                return pickle.loads(zlib.decompress(f.read()))
        except:
            return None