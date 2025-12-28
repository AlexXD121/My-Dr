"""
Data Encryption Service for Medical Information
Handles encryption/decryption of sensitive user data
"""

import os
import base64
import json
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import secrets

class EncryptionService:
    """Service for encrypting and decrypting sensitive medical data"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get encryption key from environment or create a new one"""
        # Try to get key from environment variable
        key_b64 = os.getenv('MEDICAL_DATA_ENCRYPTION_KEY')
        
        if key_b64:
            try:
                return base64.urlsafe_b64decode(key_b64)
            except Exception as e:
                print(f"⚠️ Invalid encryption key in environment: {e}")
        
        # Generate new key if not found
        print("🔐 Generating new encryption key for medical data")
        key = Fernet.generate_key()
        
        # Save to environment (in production, this should be stored securely)
        key_b64 = base64.urlsafe_b64encode(key).decode()
        print(f"🔑 Set MEDICAL_DATA_ENCRYPTION_KEY environment variable to: {key_b64}")
        
        return key
    
    def encrypt_data(self, data: Union[str, Dict, Any]) -> str:
        """Encrypt sensitive data"""
        try:
            # Convert data to JSON string if it's not already a string
            if not isinstance(data, str):
                data_str = json.dumps(data, default=str)
            else:
                data_str = data
            
            # Encrypt the data
            encrypted_data = self.fernet.encrypt(data_str.encode())
            
            # Return base64 encoded encrypted data
            return base64.urlsafe_b64encode(encrypted_data).decode()
            
        except Exception as e:
            print(f"❌ Encryption error: {e}")
            raise ValueError("Failed to encrypt data")
    
    def decrypt_data(self, encrypted_data: str) -> Any:
        """Decrypt sensitive data"""
        try:
            # Decode base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            
            # Decrypt the data
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            decrypted_str = decrypted_bytes.decode()
            
            # Try to parse as JSON, return as string if it fails
            try:
                return json.loads(decrypted_str)
            except json.JSONDecodeError:
                return decrypted_str
                
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            raise ValueError("Failed to decrypt data")
    
    def encrypt_medical_record(self, medical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive fields in medical record"""
        sensitive_fields = [
            'allergies', 'medications', 'conditions', 'notes', 
            'test_results', 'diagnosis', 'treatment_plan'
        ]
        
        encrypted_record = medical_data.copy()
        
        for field in sensitive_fields:
            if field in encrypted_record and encrypted_record[field]:
                encrypted_record[field] = self.encrypt_data(encrypted_record[field])
                encrypted_record[f'{field}_encrypted'] = True
        
        return encrypted_record
    
    def decrypt_medical_record(self, encrypted_record: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive fields in medical record"""
        sensitive_fields = [
            'allergies', 'medications', 'conditions', 'notes', 
            'test_results', 'diagnosis', 'treatment_plan'
        ]
        
        decrypted_record = encrypted_record.copy()
        
        for field in sensitive_fields:
            if f'{field}_encrypted' in decrypted_record and decrypted_record.get(f'{field}_encrypted'):
                if field in decrypted_record:
                    decrypted_record[field] = self.decrypt_data(decrypted_record[field])
                    # Remove encryption flag
                    del decrypted_record[f'{field}_encrypted']
        
        return decrypted_record

class DataRetentionService:
    """Service for managing data retention policies"""
    
    def __init__(self):
        self.default_retention_period = timedelta(days=730)  # 2 years
        self.retention_policies = {
            '1year': timedelta(days=365),
            '2years': timedelta(days=730),
            '5years': timedelta(days=1825),
            'indefinite': None
        }
    
    def get_retention_period(self, policy: str) -> Optional[timedelta]:
        """Get retention period for a policy"""
        return self.retention_policies.get(policy, self.default_retention_period)
    
    def should_delete_data(self, created_at: datetime, retention_policy: str) -> bool:
        """Check if data should be deleted based on retention policy"""
        retention_period = self.get_retention_period(retention_policy)
        
        if retention_period is None:  # Indefinite retention
            return False
        
        return datetime.utcnow() - created_at > retention_period
    
    def get_data_expiry_date(self, created_at: datetime, retention_policy: str) -> Optional[datetime]:
        """Get the expiry date for data based on retention policy"""
        retention_period = self.get_retention_period(retention_policy)
        
        if retention_period is None:  # Indefinite retention
            return None
        
        return created_at + retention_period

class AuditLogger:
    """Service for logging security-sensitive operations"""
    
    def __init__(self):
        self.log_file = os.getenv('SECURITY_AUDIT_LOG', 'security_audit.log')
    
    def log_access(self, user_id: str, resource: str, action: str, 
                   ip_address: str = None, user_agent: str = None, 
                   success: bool = True, details: Dict[str, Any] = None):
        """Log access to sensitive resources"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'success': success,
            'details': details or {}
        }
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"❌ Failed to write audit log: {e}")
    
    def log_data_access(self, user_id: str, data_type: str, operation: str, 
                       record_count: int = 1, ip_address: str = None):
        """Log access to medical data"""
        self.log_access(
            user_id=user_id,
            resource=f"medical_data_{data_type}",
            action=operation,
            ip_address=ip_address,
            details={
                'data_type': data_type,
                'record_count': record_count
            }
        )
    
    def log_profile_access(self, user_id: str, operation: str, 
                          fields_accessed: list = None, ip_address: str = None):
        """Log access to user profile"""
        self.log_access(
            user_id=user_id,
            resource="user_profile",
            action=operation,
            ip_address=ip_address,
            details={
                'fields_accessed': fields_accessed or []
            }
        )
    
    def log_authentication(self, user_id: str, action: str, success: bool,
                          ip_address: str = None, user_agent: str = None,
                          failure_reason: str = None):
        """Log authentication events"""
        details = {}
        if not success and failure_reason:
            details['failure_reason'] = failure_reason
        
        self.log_access(
            user_id=user_id,
            resource="authentication",
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=details
        )

class DataIsolationService:
    """Service for ensuring user data isolation"""
    
    @staticmethod
    def verify_user_access(user_id: str, resource_user_id: str) -> bool:
        """Verify that user can access the resource"""
        return user_id == resource_user_id
    
    @staticmethod
    def filter_user_data(query, user_id: str, user_id_field: str = 'user_id'):
        """Filter query to only return data for the specified user"""
        return query.filter(getattr(query.column_descriptions[0]['type'], user_id_field) == user_id)
    
    @staticmethod
    def validate_data_ownership(user_id: str, data_owner_id: str, resource_name: str = "resource"):
        """Validate that user owns the data they're trying to access"""
        if user_id != data_owner_id:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: You don't have permission to access this {resource_name}"
            )

class PrivacyControlService:
    """Service for managing privacy controls and data sharing preferences"""
    
    def __init__(self):
        self.default_privacy_settings = {
            'share_data_for_research': False,
            'allow_analytics': True,
            'data_retention_period': '2years',
            'allow_third_party_integrations': False,
            'marketing_communications': False
        }
    
    def get_user_privacy_settings(self, user) -> Dict[str, Any]:
        """Get user's privacy settings with defaults"""
        if hasattr(user, 'privacy_settings') and user.privacy_settings:
            settings = user.privacy_settings.copy()
            # Fill in any missing settings with defaults
            for key, default_value in self.default_privacy_settings.items():
                if key not in settings:
                    settings[key] = default_value
            return settings
        return self.default_privacy_settings.copy()
    
    def can_use_for_analytics(self, user) -> bool:
        """Check if user data can be used for analytics"""
        settings = self.get_user_privacy_settings(user)
        return settings.get('allow_analytics', True)
    
    def can_share_for_research(self, user) -> bool:
        """Check if user data can be shared for research"""
        settings = self.get_user_privacy_settings(user)
        return settings.get('share_data_for_research', False)
    
    def get_data_retention_policy(self, user) -> str:
        """Get user's data retention policy"""
        settings = self.get_user_privacy_settings(user)
        return settings.get('data_retention_period', '2years')
    
    def anonymize_user_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize user data for research/analytics"""
        anonymized = data.copy()
        
        # Remove or hash identifying information
        sensitive_fields = [
            'email', 'phone', 'display_name', 'firebase_uid',
            'ip_address', 'user_agent', 'photo_url'
        ]
        
        for field in sensitive_fields:
            if field in anonymized:
                if field == 'email':
                    # Keep domain for analytics but hash local part
                    email = anonymized[field]
                    if '@' in email:
                        local, domain = email.split('@', 1)
                        anonymized[field] = f"user_{hash(local) % 10000}@{domain}"
                else:
                    del anonymized[field]
        
        # Add anonymization timestamp
        anonymized['anonymized_at'] = datetime.utcnow().isoformat()
        
        return anonymized

# Global service instances
encryption_service = EncryptionService()
data_retention_service = DataRetentionService()
audit_logger = AuditLogger()
data_isolation_service = DataIsolationService()
privacy_control_service = PrivacyControlService()

# Utility functions for easy access
def encrypt_sensitive_data(data: Any) -> str:
    """Encrypt sensitive data"""
    return encryption_service.encrypt_data(data)

def decrypt_sensitive_data(encrypted_data: str) -> Any:
    """Decrypt sensitive data"""
    return encryption_service.decrypt_data(encrypted_data)

def log_data_access(user_id: str, data_type: str, operation: str, 
                   record_count: int = 1, ip_address: str = None):
    """Log access to sensitive data"""
    audit_logger.log_data_access(user_id, data_type, operation, record_count, ip_address)

def verify_data_ownership(user_id: str, data_owner_id: str, resource_name: str = "resource"):
    """Verify user owns the data"""
    data_isolation_service.validate_data_ownership(user_id, data_owner_id, resource_name)