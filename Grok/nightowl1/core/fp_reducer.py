from sklearn.ensemble import IsolationForest
from core.error_handler import ErrorHandler

class FalsePositiveReducer:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05)
        self.features = ['response_length', 'status_code', 'word_count', 'entropy']

    def train(self, training_data):
        try:
            feature_vectors = [[d.get(f, 0) for f in self.features] for d in training_data]
            self.model.fit(feature_vectors)
        except Exception as e:
            ErrorHandler.log_error(f"False positive reducer training failed: {str(e)}")

    def predict(self, finding):
        try:
            feature_vec = [finding.get(f, 0) for f in self.features]
            return self.model.predict([feature_vec])[0] == 1
        except Exception as e:
            ErrorHandler.log_error(f"False positive prediction failed: {str(e)}")
            return False