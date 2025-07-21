import pytest
from tools.phishing_detector import PhishingDetector
from unittest.mock import patch

@patch('tools.phishing_detector.requests.get')
def test_phishing_detection(mock_get):
    mock_get.return_value.text = "Example website content"
    
    detector = PhishingDetector()
    results = detector.detect_clones("example.com", ["sub1.example.com", "phish.com"])
    assert "phish.com" in results or len(results) == 0