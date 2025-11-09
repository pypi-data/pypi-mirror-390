"""
Django adapter for securekit
"""

import logging
from typing import Any
from django.db import models
from django.conf import settings
from django.utils.functional import cached_property

from securekit.crypto.aead import aead_encrypt, aead_decrypt
from securekit.kms.base import KeyManager

logger = logging.getLogger(__name__)

class SecureKitMiddleware:
    """Django middleware for request/response encryption"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.key_manager = self._get_key_manager()
    
    def _get_key_manager(self) -> KeyManager:
        """Get KeyManager from Django settings"""
        if not hasattr(settings, 'SECUREKIT_KEY_MANAGER'):
            raise RuntimeError("SECUREKIT_KEY_MANAGER not configured in settings")
        return settings.SECUREKIT_KEY_MANAGER
    
    def __call__(self, request):
        # Process request
        response = self.get_response(request)
        return response

class EncryptedField(models.Field):
    """Django model field for encrypted data storage"""
    
    description = "Encrypted field using securekit"
    
    def __init__(self, *args, key_id: str = "default", **kwargs):
        self.key_id = key_id
        super().__init__(*args, **kwargs)
    
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['key_id'] = self.key_id
        return name, path, args, kwargs
    
    def get_internal_type(self):
        return "BinaryField"
    
    @cached_property
    def _key_manager(self) -> KeyManager:
        """Get KeyManager from Django settings"""
        if not hasattr(settings, 'SECUREKIT_KEY_MANAGER'):
            raise RuntimeError("SECUREKIT_KEY_MANAGER not configured in settings")
        return settings.SECUREKIT_KEY_MANAGER
    
    def from_db_value(self, value: bytes, expression, connection) -> Any:
        """Convert database value to Python value"""
        if value is None:
            return value
        
        try:
            key = self._key_manager.get_key(self.key_id)
            decrypted = aead_decrypt(key, value)
            # Assume stored as JSON for complex types
            return decrypted.decode('utf-8')  # Or json.loads() for complex objects
        except Exception as e:
            logger.error(f"Field decryption failed: {e}")
            raise
    
    def to_python(self, value: Any) -> Any:
        """Convert Python value to database value"""
        if value is None or isinstance(value, bytes):
            return value
        
        # For non-bytes values, encrypt them
        key = self._key_manager.get_key(self.key_id)
        if isinstance(value, str):
            plaintext = value.encode('utf-8')
        else:
            import json
            plaintext = json.dumps(value).encode('utf-8')
        
        return aead_encrypt(key, plaintext, key_id=self.key_id)
    
    def get_prep_value(self, value: Any) -> bytes:
        """Convert Python value to query value"""
        return self.to_python(value)