"""
Abstract base class for Key Management Service adapters
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class KeyManager(ABC):
    """
    Pluggable Key Management Service interface.
    
    All key managers must implement this interface for securekit compatibility.
    """
    
    @abstractmethod
    def generate_key(self, purpose: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a new cryptographic key.
        
        Args:
            purpose: Key purpose (e.g., 'encryption', 'signing')
            metadata: Additional key metadata
            
        Returns:
            Key identifier
        """
        pass
    
    @abstractmethod
    def get_key(self, key_id: str) -> bytes:
        """
        Retrieve key material by ID.
        
        Args:
            key_id: Key identifier
            
        Returns:
            Key material as bytes
        """
        pass
    
    @abstractmethod
    def wrap_key(self, key: bytes, kek_id: str) -> bytes:
        """
        Wrap (encrypt) a key using specified Key Encryption Key.
        
        Args:
            key: Key to wrap
            kek_id: Key Encryption Key identifier
            
        Returns:
            Wrapped key
        """
        pass
    
    @abstractmethod
    def unwrap_key(self, wrapped_key: bytes, kek_id: str) -> bytes:
        """
        Unwrap (decrypt) a key.
        
        Args:
            wrapped_key: Wrapped key
            kek_id: Key Encryption Key identifier
            
        Returns:
            Unwrapped key
        """
        pass
    
    @abstractmethod
    def rotate_key(self, key_id: str) -> str:
        """
        Rotate key, return new key ID.
        
        Args:
            key_id: Old key identifier
            
        Returns:
            New key identifier
        """
        pass
    
    @abstractmethod
    def list_keys(self, purpose: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available keys with metadata.
        
        Args:
            purpose: Optional filter by key purpose
            
        Returns:
            List of key metadata dictionaries
        """
        pass
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on key manager.
        
        Returns:
            Health status information
        """
        return {"status": "unknown", "message": "Health check not implemented"}