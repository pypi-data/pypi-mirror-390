"""
FastAPI adapter for securekit
"""

import json
import logging
from typing import List, Optional, Any
from fastapi import FastAPI, Request, Response, Depends
from fastapi.routing import APIRoute

from securekit.crypto.aead import aead_encrypt, aead_decrypt
from securekit.kms.base import KeyManager

logger = logging.getLogger(__name__)

class SecureKitDependency:
    """FastAPI dependency for SecureKit utilities"""
    
    def __init__(self, key_manager: KeyManager):
        self.key_manager = key_manager
    
    # FIX: Remove async from these methods since they're not truly async
    def encrypt(self, data: bytes, key_id: str = "default") -> bytes:
        """Encrypt data"""
        key = self.key_manager.get_key(key_id)
        return aead_encrypt(key, data, key_id=key_id)
    
    def decrypt(self, ciphertext: bytes, key_id: Optional[str] = None) -> bytes:
        """Decrypt data"""
        if key_id:
            key = self.key_manager.get_key(key_id)
        else:
            # Extract from blob
            key_id = self._extract_key_id(ciphertext)
            key = self.key_manager.get_key(key_id)
        
        return aead_decrypt(key, ciphertext)
    
    def _extract_key_id(self, blob: bytes) -> str:
        """Extract key ID from ciphertext blob"""
        key_id_len = blob[4]
        return blob[5:5+key_id_len].decode('utf-8')

def securekit_dependency(key_manager: KeyManager) -> SecureKitDependency:
    """Create SecureKit dependency for FastAPI"""
    return SecureKitDependency(key_manager)

def encrypt_response(fields: List[str], key_id: str = "default"):
    """
    Decorator to encrypt response fields in FastAPI routes
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            response = await func(*args, **kwargs)
            
            if not isinstance(response, dict):
                return response
            
            # This would need to be integrated with FastAPI's dependency system
            # For actual implementation, we'd use a middleware or response model
            return response
        
        return wrapper
    return decorator

def register_securekit(app: FastAPI, key_manager: KeyManager):
    """Register SecureKit with FastAPI application"""
    # Add dependency
    app.dependency_overrides[SecureKitDependency] = lambda: securekit_dependency(key_manager)
    logger.info("SecureKit registered with FastAPI application")