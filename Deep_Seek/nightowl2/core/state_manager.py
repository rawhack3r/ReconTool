import pickle
import os
import zlib
import json
from datetime import datetime

class StateManager:
    @staticmethod
    def save_state(target, state_data):
        """Save compressed state"""
        state_dir = "state"
        os.makedirs(state_dir, exist_ok=True)
        state_file = os.path.join(state_dir, f"{target}.state")
        
        # Add timestamp
        state_data['last_saved'] = datetime.now().isoformat()
        
        # Compress
        compressed = zlib.compress(pickle.dumps(state_data))
        with open(state_file, "wb") as f:
            f.write(compressed)
        
        return state_file
    
    @staticmethod
    def load_state(target):
        """Load compressed state"""
        state_file = os.path.join("state", f"{target}.state")
        if not os.path.exists(state_file):
            return None
        
        try:
            with open(state_file, "rb") as f:
                compressed = f.read()
                return pickle.loads(zlib.decompress(compressed))
        except:
            return None
    
    @staticmethod
    def export_state_json(target):
        """Export state as human-readable JSON"""
        state = StateManager.load_state(target)
        if not state:
            return None
        
        export_dir = "outputs/state_exports"
        os.makedirs(export_dir, exist_ok=True)
        export_path = os.path.join(export_dir, f"{target}_state.json")
        
        with open(export_path, "w") as f:
            json.dump(state, f, indent=2)
        
        return export_path