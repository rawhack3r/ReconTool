import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class MLVulnerabilityAnalyzer:
    def __init__(self):
        self.model = None
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.cluster_severity = {}
    
    def train(self, vulnerability_data):
        if not vulnerability_data:
            return
        
        descriptions = [vuln["description"] for vuln in vulnerability_data]
        severities = [vuln["severity"] for vuln in vulnerability_data]
        
        severity_map = {"critical": 3, "high": 2, "medium": 1, "low": 0}
        y = np.array([severity_map.get(s, 0) for s in severities])
        
        X = self.vectorizer.fit_transform(descriptions)
        
        self.model = KMeans(n_clusters=4, random_state=42)
        self.model.fit(X)
        
        for i in range(4):
            cluster_indices = np.where(self.model.labels_ == i)[0]
            if len(cluster_indices) > 0:
                cluster_severity = np.mean(y[cluster_indices])
                self.cluster_severity[i] = cluster_severity
    
    def predict_severity(self, vulnerability_description):
        if not self.model:
            return "medium"
        
        X = self.vectorizer.transform([vulnerability_description])
        cluster = self.model.predict(X)[0]
        severity_value = self.cluster_severity.get(cluster, 1)
        
        if severity_value > 2.5:
            return "critical"
        elif severity_value > 1.5:
            return "high"
        elif severity_value > 0.5:
            return "medium"
        else:
            return "low"