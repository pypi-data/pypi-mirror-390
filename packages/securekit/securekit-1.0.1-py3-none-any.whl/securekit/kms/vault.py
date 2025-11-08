"""
HashiCorp Vault adapter implementation
"""

import logging
import time  # FIX: Add missing import
from base64 import b64encode, b64decode  # FIX: Add missing imports
from typing import Dict, Any, List, Optional
from securekit.kms.base import KeyManager

logger = logging.getLogger(__name__)

class VaultKeyManager(KeyManager):
    """HashiCorp Vault adapter for securekit"""
    
    def __init__(self, url: str, token: str, mount_point: str = "transit"):
        """
        Initialize Vault adapter.
        
        Args:
            url: Vault server URL
            token: Vault authentication token
            mount_point: Transit engine mount point
        """
        self.url = url
        self.token = token
        self.mount_point = mount_point
        self._client = None
        logger.info(f"VaultKeyManager initialized: url={url}, mount_point={mount_point}")
    
    def _get_client(self):
        """Get HVAC client (lazy initialization)"""
        if self._client is None:
            try:
                import hvac
                self._client = hvac.Client(url=self.url, token=self.token)
                if not self._client.is_authenticated():
                    raise RuntimeError("Vault authentication failed")
            except ImportError:
                raise RuntimeError("hvac required for Vault support")
            except Exception as e:
                logger.error(f"Failed to initialize Vault client: {e}")
                raise RuntimeError(f"Vault client initialization failed: {str(e)}")
        return self._client
    
    def generate_key(self, purpose: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate key in Vault transit"""
        try:
            client = self._get_client()
            key_name = f"securekit-{purpose}-{int(time.time())}"
            
            client.secrets.transit.create_key(
                name=key_name,
                type="aes256-gcm96",
                derived=False
            )
            logger.info(f"Generated Vault key: {key_name}")
            return key_name
        except Exception as e:
            logger.error(f"Vault key generation failed: {e}")
            raise RuntimeError(f"Key generation failed: {str(e)}")
    
    def get_key(self, key_id: str) -> bytes:
        """Get key material (not directly available in Vault)"""
        raise NotImplementedError("Vault does not expose raw key material")
    
    def wrap_key(self, key: bytes, kek_id: str) -> bytes:
        """Wrap key using Vault transit"""
        try:
            client = self._get_client()
            response = client.secrets.transit.encrypt_data(
                name=kek_id,
                plaintext=b64encode(key).decode('utf-8')
            )
            return response['data']['ciphertext'].encode('utf-8')
        except Exception as e:
            logger.error(f"Vault key wrapping failed: {e}")
            raise RuntimeError(f"Key wrapping failed: {str(e)}")
    
    def unwrap_key(self, wrapped_key: bytes, kek_id: str) -> bytes:
        """Unwrap key using Vault transit"""
        try:
            client = self._get_client()
            response = client.secrets.transit.decrypt_data(
                name=kek_id,
                ciphertext=wrapped_key.decode('utf-8')
            )
            return b64decode(response['data']['plaintext'])
        except Exception as e:
            logger.error(f"Vault key unwrapping failed: {e}")
            raise RuntimeError(f"Key unwrapping failed: {str(e)}")
    
    def rotate_key(self, key_id: str) -> str:
        """Rotate Vault key"""
        try:
            client = self._get_client()
            client.secrets.transit.rotate_key(name=key_id)
            logger.info(f"Rotated Vault key: {key_id}")
            return key_id
        except Exception as e:
            logger.error(f"Vault key rotation failed: {e}")
            raise RuntimeError(f"Key rotation failed: {str(e)}")
    
    def list_keys(self, purpose: Optional[str] = None) -> List[Dict[str, Any]]:
        """List Vault keys"""
        try:
            client = self._get_client()
            response = client.secrets.transit.list_keys()
            keys = []
            for key_name in response['data']['keys']:
                keys.append({'key_id': key_name})
            return keys
        except Exception as e:
            logger.error(f"Vault list keys failed: {e}")
            raise RuntimeError(f"List keys failed: {str(e)}")