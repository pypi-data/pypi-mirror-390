"""
AWS Key Management Service adapter
"""

import logging
from typing import Dict, Any, List, Optional
from securekit.kms.base import KeyManager
try:
    import boto3
except ImportError:
    boto3 = None
    
logger = logging.getLogger(__name__)

class AWSKeyManager(KeyManager):
    """AWS KMS adapter for securekit"""
    
    def __init__(self, region: str = None, profile: str = None):
        """
        Initialize AWS KMS adapter.
        
        Args:
            region: AWS region (default: from environment)
            profile: AWS profile (default: from environment)
        """
        self.region = region
        self.profile = profile
        self._client = None
        logger.info(f"AWSKeyManager initialized: region={region}")
    
    def _get_client(self):
        """Get boto3 KMS client (lazy initialization)"""
        if self._client is None:
            try:
                import boto3
                session = boto3.Session(profile_name=self.profile)
                self._client = session.client('kms', region_name=self.region)
            except ImportError:
                raise RuntimeError("boto3 required for AWS KMS support")
            except Exception as e:
                logger.error(f"Failed to initialize AWS KMS client: {e}")
                raise RuntimeError(f"AWS KMS client initialization failed: {str(e)}")
        return self._client
    
    def generate_key(self, purpose: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate AWS KMS key"""
        try:
            client = self._get_client()
            response = client.create_key(
                Description=f"securekit: {purpose}",
                KeyUsage='ENCRYPT_DECRYPT',
                Origin='AWS_KMS'
            )
            key_id = response['KeyMetadata']['KeyId']
            logger.info(f"Generated AWS KMS key: {key_id}")
            return key_id
        except Exception as e:
            logger.error(f"AWS KMS key generation failed: {e}")
            raise RuntimeError(f"Key generation failed: {str(e)}")
    
    def get_key(self, key_id: str) -> bytes:
        """Get key material (not directly available in AWS KMS)"""
        raise NotImplementedError("AWS KMS does not expose raw key material")
    
    def wrap_key(self, key: bytes, kek_id: str) -> bytes:
        """Wrap key using AWS KMS"""
        try:
            client = self._get_client()
            response = client.encrypt(
                KeyId=kek_id,
                Plaintext=key
            )
            return response['CiphertextBlob']
        except Exception as e:
            logger.error(f"AWS KMS key wrapping failed: {e}")
            raise RuntimeError(f"Key wrapping failed: {str(e)}")
    
    def unwrap_key(self, wrapped_key: bytes, kek_id: str) -> bytes:
        """Unwrap key using AWS KMS"""
        try:
            client = self._get_client()
            response = client.decrypt(
                KeyId=kek_id,
                CiphertextBlob=wrapped_key
            )
            return response['Plaintext']
        except Exception as e:
            logger.error(f"AWS KMS key unwrapping failed: {e}")
            raise RuntimeError(f"Key unwrapping failed: {str(e)}")
    
    def rotate_key(self, key_id: str) -> str:
        """Rotate AWS KMS key"""
        try:
            client = self._get_client()
            # AWS KMS automatically rotates keys every year
            # This enables immediate key rotation
            client.enable_key_rotation(KeyId=key_id)
            logger.info(f"Enabled key rotation for: {key_id}")
            return key_id
        except Exception as e:
            logger.error(f"AWS KMS key rotation failed: {e}")
            raise RuntimeError(f"Key rotation failed: {str(e)}")
    
    def list_keys(self, purpose: Optional[str] = None) -> List[Dict[str, Any]]:
        """List AWS KMS keys"""
        try:
            client = self._get_client()
            response = client.list_keys()
            keys = []
            for key in response['Keys']:
                keys.append({
                    'key_id': key['KeyId'],
                    'arn': key['KeyArn']
                })
            return keys
        except Exception as e:
            logger.error(f"AWS KMS list keys failed: {e}")
            raise RuntimeError(f"List keys failed: {str(e)}")