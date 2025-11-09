# [file name]: local.py
# [file content begin]
"""
Local encrypted file-based key store implementation
"""

import os
import json
import time
import logging
from base64 import b64encode, b64decode
from typing import Dict, Any, List, Optional
from securekit.crypto.aead import aead_encrypt, aead_decrypt
from securekit.crypto.core import secure_random, hkdf_derive
from securekit.kms.base import KeyManager

logger = logging.getLogger(__name__)

class LocalKeyManager(KeyManager):
    """
    Local encrypted file-based key store.
    
    WARNING: For development and testing only. Use HSMs or cloud KMS in production.
    """
    
    def __init__(self, keystore_path: str, master_key: Optional[bytes] = None):
        """
        Initialize local key manager.
        
        Args:
            keystore_path: Path to keystore JSON file
            master_key: Optional master key for encryption (auto-generated if not provided)
        """
        self.keystore_path = os.path.expanduser(keystore_path)  # FIX: Expand ~ to home directory
        self.master_key = master_key or self._load_or_create_master_key()
        self._keys = self._load_keystore()
        
        logger.info(f"LocalKeyManager initialized: keystore_path={keystore_path}, "
                   f"keys_loaded={len(self._keys)}")
    
    def _ensure_directory_exists(self, filepath: str) -> None:
        """Ensure the directory for a file exists"""
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, mode=0o700)
            logger.debug(f"Created directory: {directory}")
    
    def _load_or_create_master_key(self) -> bytes:
        """Load or create secure master key"""
        master_key_path = self.keystore_path + ".master"
        
        try:
            # FIX: Ensure directory exists before file operations
            self._ensure_directory_exists(master_key_path)
            
            if os.path.exists(master_key_path):
                # Security: Load existing master key
                with open(master_key_path, 'rb') as f:
                    master_key = f.read()
                if len(master_key) == 32:
                    logger.debug("Loaded existing master key")
                    return master_key
            
            # Security: Generate new master key
            master_key = secure_random(32)
            with open(master_key_path, 'wb') as f:
                f.write(master_key)
            # Security: Restrict file permissions
            os.chmod(master_key_path, 0o600)
            logger.info("Generated new master key")
            return master_key
            
        except Exception as e:
            logger.error(f"Failed to load/create master key: {e}")
            raise RuntimeError(f"Master key initialization failed: {str(e)}")
    
    def _load_keystore(self) -> Dict[str, Any]:
        """Load encrypted keystore from file"""
        try:
            if os.path.exists(self.keystore_path):
                with open(self.keystore_path, 'r') as f:
                    data = json.load(f)
                logger.debug(f"Loaded keystore with {len(data.get('keys', {}))} keys")
                return data.get('keys', {})
            return {}
        except json.JSONDecodeError as e:
            # FIX: Handle empty or corrupted keystore file
            logger.warning(f"Keystore file is empty or corrupted, starting fresh: {e}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load keystore: {e}")
            return {}
    
    def _save_keystore(self) -> None:
        """Save encrypted keystore to file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.keystore_path) or '.', exist_ok=True)
            
            data = {
                'version': '1.0',
                'created_at': time.time(),
                'keys': self._keys
            }
            
            with open(self.keystore_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Security: Restrict file permissions
            os.chmod(self.keystore_path, 0o600)
            logger.debug("Saved keystore to disk")
            
        except Exception as e:
            logger.error(f"Failed to save keystore: {e}")
            raise RuntimeError(f"Keystore save failed: {str(e)}")
    
    def _derive_key_encryption_key(self, key_id: str) -> bytes:
        """Derive a unique key encryption key for each key"""
        # Security: Use HKDF to derive unique KEK for each key
        return hkdf_derive(
            salt=self.master_key,
            ikm=key_id.encode('utf-8'),
            info=b'local_keystore_kek',
            length=32
        )
    
    def generate_key(self, purpose: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate and store new key"""
        try:
            key_id = f"key_{int(time.time())}_{len(self._keys)}"
            key_material = secure_random(32)  # 256-bit key
            
            # Security: Derive unique KEK for this key
            kek = self._derive_key_encryption_key(key_id)
            
            # Encrypt key material
            encrypted_key = aead_encrypt(kek, key_material, key_id=key_id)
            
            self._keys[key_id] = {
                'purpose': purpose,
                'encrypted_key': b64encode(encrypted_key).decode('utf-8'),
                'metadata': metadata or {},
                'created_at': time.time(),
                'version': 1,
                'retired': False  # FIX: Add retired flag
            }
            
            self._save_keystore()
            logger.info(f"Generated new key: id={key_id}, purpose={purpose}")
            
            return key_id
            
        except Exception as e:
            logger.error(f"Key generation failed: {e}")
            raise RuntimeError(f"Key generation failed: {str(e)}")
    
    def get_key(self, key_id: str) -> bytes:
        """Retrieve decrypted key material"""
        if key_id not in self._keys:
            logger.warning(f"Key not found: {key_id}")
            raise KeyError(f"Key not found: {key_id}")
        
        try:
            encrypted_key = b64decode(self._keys[key_id]['encrypted_key'])
            kek = self._derive_key_encryption_key(key_id)
            
            key_material = aead_decrypt(kek, encrypted_key)
            logger.debug(f"Retrieved key: {key_id}")
            
            return key_material
            
        except Exception as e:
            logger.error(f"Key retrieval failed for {key_id}: {e}")
            raise RuntimeError(f"Key retrieval failed: {str(e)}")
    
    def wrap_key(self, key: bytes, kek_id: str) -> bytes:
        """Wrap key using specified KEK"""
        try:
            kek = self.get_key(kek_id)
            wrapped = aead_encrypt(kek, key, key_id=kek_id)
            logger.debug(f"Wrapped key using KEK: {kek_id}")
            return wrapped
        except Exception as e:
            logger.error(f"Key wrapping failed: {e}")
            raise RuntimeError(f"Key wrapping failed: {str(e)}")
    
    def unwrap_key(self, wrapped_key: bytes, kek_id: str) -> bytes:
        """Unwrap key using specified KEK"""
        try:
            kek = self.get_key(kek_id)
            key = aead_decrypt(kek, wrapped_key)
            logger.debug(f"Unwrapped key using KEK: {kek_id}")
            return key
        except Exception as e:
            logger.error(f"Key unwrapping failed: {e}")
            raise RuntimeError(f"Key unwrapping failed: {str(e)}")
    
    def rotate_key(self, key_id: str) -> str:
        """Rotate key, return new key ID"""
        try:
            if key_id not in self._keys:
                raise KeyError(f"Key not found: {key_id}")
            
            old_key_data = self._keys[key_id]
            
            # Generate new key with same purpose and metadata
            new_key_id = self.generate_key(
                old_key_data['purpose'], 
                old_key_data.get('metadata', {})
            )
            
            # Mark old key as retired
            self._keys[key_id]['retired'] = True
            self._keys[key_id]['replaced_by'] = new_key_id
            self._keys[key_id]['retired_at'] = time.time()
            
            # FIX: Save the keystore after marking old key as retired
            self._save_keystore()
            
            logger.info(f"Rotated key: {key_id} -> {new_key_id}")
            
            return new_key_id
            
        except Exception as e:
            logger.error(f"Key rotation failed for {key_id}: {e}")
            raise RuntimeError(f"Key rotation failed: {str(e)}")
    
    def list_keys(self, purpose: Optional[str] = None, include_retired: bool = False) -> List[Dict[str, Any]]:
        """List available keys with metadata"""
        keys = []
        for key_id, key_data in self._keys.items():
            # Filter by purpose if specified
            if purpose and key_data.get('purpose') != purpose:
                continue
            
            # Filter out retired keys unless explicitly included
            if not include_retired and key_data.get('retired', False):
                continue
                
            keys.append({
                'key_id': key_id,
                'purpose': key_data.get('purpose'),
                'created_at': key_data.get('created_at'),
                'metadata': key_data.get('metadata', {}),
                'retired': key_data.get('retired', False),
                'replaced_by': key_data.get('replaced_by'),
                'retired_at': key_data.get('retired_at')
            })
        
        return keys
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            self._save_keystore()
            return {
                "status": "healthy",
                "keys_count": len(self._keys),
                "keystore_path": self.keystore_path
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
# [file content end]