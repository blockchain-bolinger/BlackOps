#!/usr/bin/env python3
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import os

class CVEClassifier:
    """Lernt aus CVE-Beschreibungen den Schweregrad (CVSS)."""

    def __init__(self, model_path="ai/models/cve_classifier.pkl"):
        self.model_path = model_path
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(model_path.replace('.pkl', '_vectorizer.pkl'))
        else:
            self.model = None
            self.vectorizer = None

    def train(self, descriptions, severities):
        """Trainiert das Modell (severities: 'low','medium','high','critical')."""
        self.vectorizer = TfidfVectorizer(max_features=1000)
        X = self.vectorizer.fit_transform(descriptions)
        self.model = RandomForestClassifier()
        self.model.fit(X, severities)
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.vectorizer, self.model_path.replace('.pkl', '_vectorizer.pkl'))

    def predict(self, description):
        if not self.model:
            return "unknown"
        X = self.vectorizer.transform([description])
        return self.model.predict(X)[0]

# Beispiel-Daten zum Trainieren
if __name__ == "__main__":
    sample_descriptions = [
        "Buffer overflow in Apache HTTP Server 2.4.49 allows remote code execution",
        "Cross-site scripting in WordPress plugin",
        "SQL injection in phpMyAdmin",
        "Kernel privilege escalation in Linux",
    ]
    sample_severities = ["high", "medium", "high", "critical"]
    clf = CVEClassifier()
    clf.train(sample_descriptions, sample_severities)
    print(clf.predict("Remote code execution in Apache"))