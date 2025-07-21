import json
import os
import pickle
from datetime import datetime

class StateManager:
    @staticmethod
    def save_state(target, state_data):
        """Save current scan state to file"""
        state_dir = "state"
        os.makedirs(state_dir, exist_ok=True)
        state_file = os.path.join(state_dir, f"{target}.state")
        
        # Add timestamp
        state_data['last_saved'] = datetime.now().isoformat()
        
        with open(state_file, "wb") as f:
            pickle.dump(state_data, f)
        
        return state_file
    
    @staticmethod
    def load_state(target):
        """Load scan state from file"""
        state_file = os.path.join("state", f"{target}.state")
        if not os.path.exists(state_file):
            return None
        
        try:
            with open(state_file, "rb") as f:
                return pickle.load(f)
        except:
            return None
    
    @staticmethod
    def clear_state(target):
        """Clear saved state"""
        state_file = os.path.join("state", f"{target}.state")
        if os.path.exists(state_file):
            os.remove(state_file)
            return True
        return False
    
    @staticmethod
    def get_resume_points(state):
        """Get resume points from saved state"""
        if not state:
            return {}
        
        return {
            "last_phase": state.get('current_phase', ''),
            "completed_tools": state.get('completed_tools', []),
            "progress": state.get('progress', 0)
        }