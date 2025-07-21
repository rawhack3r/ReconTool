from sklearn.ensemble import IsolationForest
import numpy as np

class FalsePositiveReducer:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05)
        self.features = ['response_length', 'status_code', 'word_count', 'entropy']
    
    def train(self, historical_findings):
        X = np.array([[f[feat] for feat in self.features] for f in historical_findings])
        self.model.fit(X)
    
    def predict(self, finding):
        feature_vec = [finding.get(f, 0) for f in self.features]
        return self.model.predict([feature_vec])[0] == 1  # 1=valid, -1=FP