import pytest
from unittest.mock import patch, MagicMock
from core.cloud_scanner import CloudScanner

@pytest.fixture
def scanner():
    return CloudScanner({})

@patch('core.cloud_scanner.boto3.Session')
def test_scan_aws(mock_session, scanner):
    mock_client = MagicMock()
    mock_session.return_value.client.return_value = mock_client
    
    # Mock AWS responses
    mock_client.list_buckets.return_value = {
        'Buckets': [{'Name': 'test-bucket'}, {'Name': 'target-bucket'}]
    }
    mock_client.get_bucket_acl.return_value = {
        'Grants': [{'Grantee': {'URI': 'http://acs.amazonaws.com/groups/global/AllUsers'}, 'Permission': 'FULL_CONTROL'}]
    }
    
    result = scanner.scan_aws("target")
    assert len(result['resources']) == 1
    assert len(result['findings']) == 1
    assert "Public S3 bucket" in result['findings'][0]['issue']

@patch('core.cloud_scanner.DefaultAzureCredential')
@patch('core.cloud_scanner.ResourceManagementClient')
def test_scan_azure(mock_client, mock_cred, scanner):
    mock_client.return_value.resources.list.return_value = [
        MagicMock(name="resource1"), 
        MagicMock(name="target-resource")
    ]
    
    result = scanner.scan_azure("target")
    assert len(result['resources']) == 1

@patch('core.cloud_scanner.resourcemanager.ProjectsClient')
def test_scan_gcp(mock_client, scanner):
    mock_client.return_value.search_projects.return_value = [
        MagicMock(display_name="project1"),
        MagicMock(display_name="target-project")
    ]
    
    result = scanner.scan_gcp("target")
    assert len(result['resources']) == 1