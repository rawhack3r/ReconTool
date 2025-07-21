import boto3
import botocore
from botocore.exceptions import ClientError
from core.error_handler import ErrorHandler

class CloudAuditor:
    def __init__(self, profile=None):
        self.session = boto3.Session(profile_name=profile)
        self.iam = self.session.client('iam')
        self.s3 = self.session.client('s3')
    
    def audit_iam(self):
        findings = []
        
        # Check for admin privileges
        policies = self.iam.list_policies(Scope='Local')['Policies']
        for policy in policies:
            policy_doc = self.iam.get_policy_version(
                PolicyArn=policy['Arn'],
                VersionId=policy['DefaultVersionId']
            )['PolicyVersion']['Document']
            
            if self.is_admin_policy(policy_doc):
                findings.append({
                    "type": "IAM Policy",
                    "name": policy['PolicyName'],
                    "issue": "Administrative privileges",
                    "severity": 10
                })
        
        # Check for inactive access keys
        users = self.iam.list_users()['Users']
        for user in users:
            keys = self.iam.list_access_keys(UserName=user['UserName'])['AccessKeyMetadata']
            for key in keys:
                if key['Status'] == 'Active':
                    last_used = self.iam.get_access_key_last_used(
                        AccessKeyId=key['AccessKeyId']
                    ).get('AccessKeyLastUsed', {})
                    if not last_used.get('LastUsedDate'):
                        findings.append({
                            "type": "Access Key",
                            "user": user['UserName'],
                            "issue": "Unused active access key",
                            "severity": 7
                        })
        return findings
    
    def audit_s3(self):
        findings = []
        buckets = self.s3.list_buckets()['Buckets']
        
        for bucket in buckets:
            bucket_name = bucket['Name']
            
            # Check public access
            try:
                acl = self.s3.get_bucket_acl(Bucket=bucket_name)
                for grant in acl['Grants']:
                    if grant['Grantee'].get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers':
                        findings.append({
                            "type": "S3 Bucket",
                            "name": bucket_name,
                            "issue": "Public read access",
                            "severity": 9
                        })
            except ClientError:
                pass
            
            # Check encryption
            try:
                encryption = self.s3.get_bucket_encryption(Bucket=bucket_name)
                if not encryption.get('ServerSideEncryptionConfiguration'):
                    findings.append({
                        "type": "S3 Bucket",
                        "name": bucket_name,
                        "issue": "No server-side encryption",
                        "severity": 8
                    })
            except ClientError:
                findings.append({
                    "type": "S3 Bucket",
                    "name": bucket_name,
                    "issue": "No server-side encryption",
                    "severity": 8
                })
        return findings
    
    def is_admin_policy(self, policy_doc):
        for statement in policy_doc.get('Statement', []):
            if statement.get('Effect') == 'Allow':
                if statement.get('Action') == '*' or statement.get('Resource') == '*':
                    return True
                if 'Action' in statement and isinstance(statement['Action'], list):
                    if 'iam:*' in statement['Action'] or '*' in statement['Action']:
                        return True
        return False

def run(target, progress_callback=None):
    auditor = CloudAuditor()
    results = {
        "iam_findings": [],
        "s3_findings": []
    }
    
    try:
        if progress_callback:
            progress_callback("CloudAudit", 20, "Auditing IAM policies...")
        results["iam_findings"] = auditor.audit_iam()
        
        if progress_callback:
            progress_callback("CloudAudit", 50, "Checking S3 buckets...")
        results["s3_findings"] = auditor.audit_s3()
        
        if progress_callback:
            progress_callback("CloudAudit", 100, "Cloud audit completed")
            
    except botocore.exceptions.NoCredentialsError:
        ErrorHandler.log_error("CloudAudit", "No AWS credentials found", target)
    except Exception as e:
        ErrorHandler.log_error("CloudAudit", str(e), target)
        raise
        
    return results