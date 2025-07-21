import pytest
from unittest.mock import patch, MagicMock
from core.ai_analyzer import AIAnalyzer

@pytest.fixture
def analyzer(config):
    return AIAnalyzer(config)

@patch("openai.ChatCompletion.create")
def test_vulnerability_analysis(mock_openai, analyzer):
    mock_openai.return_value = MagicMock(choices=[MagicMock(message={'content': 'Test analysis'})])
    result = analyzer._analyze_vulnerabilities("example.com", "Sample vulnerability data")
    assert "Test analysis" in result

@patch("transformers.pipeline")
def test_secret_classification(mock_pipeline, analyzer):
    mock_pipeline.return_value = [{'label': 'SECRET', 'score': 0.95}]
    result = analyzer._classify_secrets("api_key=abcdef1234567890")
    assert any(item['score'] > 0.9 for item in result)

@patch("openai.ChatCompletion.create")
def test_attack_path_modeling(mock_openai, analyzer):
    mock_openai.return_value = MagicMock(choices=[MagicMock(message={'content': 'Attack path'})])
    result = analyzer._model_attack_paths("example.com", "Asset data")
    assert "Attack path" in result

def test_data_extraction(analyzer):
    sample_data = {
        "vulnerabilities": {"nuclei": "SQL injection found"},
        "information": {"secrets": ["api_key=12345"]},
        "subdomains": {"amass": "admin.example.com"}
    }
    vuln_data = analyzer._extract_vulnerability_data(sample_data)
    assert "SQL injection" in vuln_data
    
    secret_data = analyzer._extract_secret_data(sample_data)
    assert "api_key" in secret_data