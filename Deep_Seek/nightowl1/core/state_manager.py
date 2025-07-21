import json
import os
import pickle
from datetime import datetime

STATE_FILE = ".nightowl_state"

def save_state(state_data, filename=STATE_FILE):
    """Save current scan state to file"""
    try:
        with open(filename, 'wb') as f:
            pickle.dump(state_data, f)
        return True
    except Exception as e:
        print(f"Error saving state: {str(e)}")
        return False

def load_state(filename=STATE_FILE):
    """Load scan state from file"""
    if not os.path.exists(filename):
        return None
        
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading state: {str(e)}")
        return None

def clear_state(filename=STATE_FILE):
    """Clear saved state"""
    if os.path.exists(filename):
        os.remove(filename)
        return True
    return False