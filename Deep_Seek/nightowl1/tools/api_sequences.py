import random
from core.error_handler import ErrorHandler

class APISequenceTester:
    def __init__(self):
        self.sequences = [
            ["register", "login", "profile"],
            ["login", "cart", "checkout"],
            ["login", "document_upload", "download"]
        ]
    
    def generate_test_cases(self, endpoints):
        """Create stateful test sequences"""
        test_cases = []
        for seq in self.sequences:
            valid_sequence = [e for e in seq if e in endpoints]
            if valid_sequence:
                test_cases.append(valid_sequence)
        
        # Add random sequences for fuzzing
        for _ in range(5):
            test_cases.append(random.sample(list(endpoints.keys()), min(3, len(endpoints))))
        
        return test_cases
    
    def execute_sequence(self, sequence, base_url):
        """Execute API sequence with state maintenance"""
        session = requests.Session()
        state = {}
        results = []
        
        for step in sequence:
            endpoint = base_url + step["path"]
            try:
                # Prepare request with current state
                request_data = self.inject_state(step["parameters"], state)
                
                # Execute request
                if step["method"] == "GET":
                    response = session.get(endpoint, params=request_data)
                else:
                    response = session.post(endpoint, json=request_data)
                
                # Save state from response
                self.extract_state(response.json(), state)
                
                results.append({
                    "step": step["name"],
                    "status": response.status_code,
                    "state": state.copy()
                })
            except Exception as e:
                ErrorHandler.log_error("APISequence", str(e), base_url)
                results.append({"step": step["name"], "error": str(e)})
        
        return results
    
    def inject_state(self, params, state):
        """Inject current state into request parameters"""
        # Implementation would replace placeholders with state values
        return params
    
    def extract_state(self, response, state):
        """Extract state values from API response"""
        # Implementation would parse response for state tokens
        pass