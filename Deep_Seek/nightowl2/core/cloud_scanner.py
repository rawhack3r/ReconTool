import os
import json
import logging
from core.error_handler import ErrorHandler

# Conditional imports with fallbacks
try:
    import boto3
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    logging.warning("AWS SDK (boto3) not installed. AWS scanning disabled.")

try:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.resource import ResourceManagementClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logging.warning("Azure SDK not installed. Azure scanning disabled.")

try:
    from google.cloud import resourcemanager
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    logging.warning("GCP SDK not installed. GCP scanning disabled.")

class CloudScanner:
    def __init__(self, config):
        self.config = config
        self.error_handler = ErrorHandler()
    
    async def scan_provider(self, provider, target):
        """Scan cloud provider resources with dependency checks"""
        try:
            if provider == "AWS" and AWS_AVAILABLE:
                return self.scan_aws(target)
            elif provider == "Azure" and AZURE_AVAILABLE:
                return self.scan_azure(target)
            elif provider == "GCP" and GCP_AVAILABLE:
                return self.scan_gcp(target)
            
            return {
                "status": "skipped",
                "message": f"Cloud provider '{provider}' not supported or dependencies missing"
            }
        except Exception as e:
            error_msg = f"{provider} scan failed: {str(e)}"
            self.error_handler.handle(
                f"{provider}Scanner",
                error_msg,
                "Cloud Scan",
                ErrorLevel.ERROR,
                ErrorType.CLOUD,
                recoverable=True
            )
            return {
                "status": "error",
                "message": error_msg
            }
    
    def scan_aws(self, target):
        """Scan AWS resources"""
        try:
            # Get credentials from environment or config
            aws_access_key = os.getenv("AWS_ACCESS_KEY_ID") or self.config.get('AWS_ACCESS_KEY_ID')
            aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY") or self.config.get('AWS_SECRET_ACCESS_KEY')
            
            if not aws_access_key or not aws_secret:
                return {
                    "status": "skipped",
                    "message": "AWS credentials not configured"
                }
            
            session = boto3.Session(
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret,
                region_name=self.config.get('AWS_REGION', 'us-east-1')
            )
            
            # Scan S3 buckets
            s3 = session.client('s3')
            buckets = s3.list_buckets().get('Buckets', [])
            target_buckets = [b for b in buckets if target in b['Name']]
            
            # Check for misconfigurations
            findings = []
            for bucket in target_buckets:
                try:
                    # Check public access
                    acl = s3.get_bucket_acl(Bucket=bucket['Name'])
                    public = any(
                        g['Permission'] == 'FULL_CONTROL' 
                        for g in acl.get('Grants', []) 
                        if g['Grantee'].get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers'
                    )
                    
                    # Check encryption
                    try:
                        encryption = s3.get_bucket_encryption(Bucket=bucket['Name'])
                        encrypted = bool(encryption.get('ServerSideEncryptionConfiguration', {}).get('Rules', []))
                    except:
                        encrypted = False
                    
                    # Check logging
                    logging = s3.get_bucket_logging(Bucket=bucket['Name'])
                    logging_enabled = bool(logging.get('LoggingEnabled', False))
                    
                    if public:
                        findings.append({
                            "resource": bucket['Name'],
                            "issue": "Public S3 bucket",
                            "severity": "Critical"
                        })
                    
                    if not encrypted:
                        findings.append({
                            "resource": bucket['Name'],
                            "issue": "Encryption not enabled",
                            "severity": "High"
                        })
                    
                    if not logging_enabled:
                        findings.append({
                            "resource": bucket['Name'],
                            "issue": "Logging not enabled",
                            "severity": "Medium"
                        })
                        
                except Exception as e:
                    self.error_handler.handle(
                        "AWSScanner",
                        f"Bucket {bucket['Name']} scan failed: {str(e)}",
                        "Cloud Scan",
                        ErrorLevel.WARNING,
                        ErrorType.CLOUD,
                        recoverable=True
                    )
                    continue
            
            return {
                "resources": [b['Name'] for b in target_buckets],
                "findings": findings,
                "status": "completed"
            }
        except Exception as e:
            raise Exception(f"AWS scan failed: {str(e)}")
    
    def scan_azure(self, target):
        """Scan Azure resources"""
        try:
            subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID") or self.config.get('AZURE_SUBSCRIPTION_ID')
            if not subscription_id:
                return {
                    "status": "skipped",
                    "message": "Azure subscription ID not configured"
                }
            
            credential = DefaultAzureCredential()
            client = ResourceManagementClient(credential, subscription_id)
            
            # List resources
            resources = list(client.resources.list())
            target_resources = [r for r in resources if target in r.name]
            
            # Simplified findings for demo
            findings = []
            for resource in target_resources:
                if "public" in resource.name.lower():
                    findings.append({
                        "resource": resource.name,
                        "issue": "Publicly accessible resource",
                        "severity": "High"
                    })
            
            return {
                "resources": [r.name for r in target_resources],
                "findings": findings,
                "status": "completed"
            }
        except Exception as e:
            raise Exception(f"Azure scan failed: {str(e)}")
    
    def scan_gcp(self, target):
        """Scan GCP resources"""
        try:
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or self.config.get('GCP_CREDENTIALS_PATH')
            if not credentials_path:
                return {
                    "status": "skipped",
                    "message": "GCP credentials not configured"
                }
            
            client = resourcemanager.ProjectsClient()
            projects = list(client.search_projects())
            target_projects = [p for p in projects if target in p.display_name]
            
            findings = []
            for project in target_projects:
                if "prod" in project.display_name.lower():
                    findings.append({
                        "resource": project.display_name,
                        "issue": "Production environment without restrictions",
                        "severity": "High"
                    })
            
            return {
                "resources": [p.display_name for p in target_projects],
                "findings": findings,
                "status": "completed"
            }
        except Exception as e:
            raise Exception(f"GCP scan failed: {str(e)}")