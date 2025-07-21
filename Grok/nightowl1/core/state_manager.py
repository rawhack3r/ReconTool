import json
from core.error_handler import ErrorHandler

class StateManager:
    def save_state(self, state_data, filename="nightowl_state.json"):
        try:
            with open(filename, 'w') as f:
                json.dump(state_data, f)
            return True
        except Exception as e:
            ErrorHandler.log_error(f"Error saving state: {str(e)}")
            return False

    def load_state(self, filename="nightowl_state.json"):
        try:
            with open(filename, 'r') as f:
                state = json.load(f)
                # Validate state
                required_keys = ['target', 'mode', 'results', 'completed_tools']
                if all(key in state for key in required_keys):
                    return state
                else:
                    ErrorHandler.log_error("Invalid state file format")
                    return None
        except FileNotFoundError:
            return None
        except Exception as e:
            ErrorHandler.log_error(f"Error loading state: {str(e)}")
            return None