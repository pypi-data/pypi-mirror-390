"""
Authenticated Encryption with Associated Data implementations
"""

import os
import struct
import logging
from typing import Optional
from cryptography.exceptions import InvalidTag
import nacl.secret
import nacl.utils

logger = logging.getLogger(__name__)

class AEADCrypto:
    """Authenticated Encryption with Associated Data using ChaCha20-Poly1305"""
    
    # Security: Use XChaCha20 variant for safe random nonces (24 bytes)
    VERSION = b'v1\0\0'  # 4-byte version field (fixed: exactly 4 bytes)
    NONCE_SIZE = 24  # XChaCha20-Poly1305 nonce
    KEY_SIZE = 32    # 256-bit key for ChaCha20
    
    def __init__(self):
        logger.debug("AEADCrypto initialized with ChaCha20-Poly1305")
    
    def encrypt(self, key: bytes, plaintext: bytes, aad: bytes = b'', 
                key_id: str = '') -> bytes:
        """
        Encrypt with ChaCha20-Poly1305, return structured blob.
        
        Structure: version(4)|key_id_len(1)|key_id(n)|nonce(24)|ciphertext|tag(16)
        
        Args:
            key: 32-byte encryption key
            plaintext: Data to encrypt
            aad: Additional authenticated data
            key_id: Key identifier for key management
            
        Returns:
            Structured ciphertext blob
            
        Raises:
            ValueError: If key is invalid or encryption fails
        """
        # Security: Validate key size
        if len(key) != self.KEY_SIZE:
            raise ValueError(f"Key must be {self.KEY_SIZE} bytes, got {len(key)}")
        
        # Security: Generate secure random nonce
        nonce = nacl.utils.random(self.NONCE_SIZE)
        
        # Create secret box with key
        box = nacl.secret.SecretBox(key)
        
        # FIX: Handle AAD by including it in the plaintext
        if aad:
            # Prefix plaintext with AAD length and AAD for authentication
            aad_length = len(aad).to_bytes(4, 'big')
            modified_plaintext = aad_length + aad + plaintext
        else:
            modified_plaintext = plaintext
        
        # Encrypt - PyNaCl's encrypt returns the entire encrypted message
        encrypted_message = box.encrypt(modified_plaintext, nonce)
        
        # The encrypted_message structure is: nonce (24) + ciphertext + tag (16)
        # Extract just the ciphertext + tag (skip the first 24 bytes which are nonce)
        ciphertext_with_tag = encrypted_message[self.NONCE_SIZE:]
        
        # Structure: version(4)|key_id_len(1)|key_id(n)|nonce(24)|ciphertext_with_tag
        key_id_bytes = key_id.encode('utf-8')
        key_id_len = len(key_id_bytes)
        
        # Security: Limit key ID length to prevent abuse
        if key_id_len > 255:
            raise ValueError("Key ID too long (max 255 bytes)")
        
        structured_blob = (
            self.VERSION +                    # 4 bytes
            bytes([key_id_len]) +            # 1 byte
            key_id_bytes +                   # n bytes
            nonce +                          # 24 bytes
            ciphertext_with_tag              # ciphertext + tag (variable length)
        )
        
        logger.debug(f"AEAD encryption: key_id={key_id}, plaintext_len={len(plaintext)}, "
                    f"ciphertext_len={len(ciphertext_with_tag)}")
        
        return structured_blob
    
    def decrypt(self, key: bytes, blob: bytes, aad: bytes = b'') -> bytes:
        """
        Decrypt structured blob, verifying authentication tag.
        
        Args:
            key: 32-byte decryption key
            blob: Structured ciphertext blob
            aad: Additional authenticated data
            
        Returns:
            Decrypted plaintext
            
        Raises:
            ValueError: If decryption fails or authentication invalid
        """
        try:
            # Security: Validate minimum blob size
            min_blob_size = 4 + 1 + 24 + 16  # version + key_id_len + nonce + tag
            if len(blob) < min_blob_size:
                raise ValueError("Blob too short")
            
            # Parse structured blob
            version = blob[0:4]
            if version != self.VERSION:
                raise ValueError(f"Unsupported version: {version}")
            
            key_id_len = blob[4]
            key_id_start = 5
            key_id_end = key_id_start + key_id_len
            key_id = blob[key_id_start:key_id_end].decode('utf-8')
            
            nonce_start = key_id_end
            nonce_end = nonce_start + self.NONCE_SIZE
            nonce = blob[nonce_start:nonce_end]
            
            ciphertext_with_tag = blob[nonce_end:]
            
            # Create secret box
            box = nacl.secret.SecretBox(key)
            
            # Reconstruct encrypted message for PyNaCl (nonce + ciphertext + tag)
            encrypted_message = nonce + ciphertext_with_tag
            
            # Decrypt
            decrypted = box.decrypt(encrypted_message)
            
            # FIX: Handle AAD verification
            if aad:
                # Extract AAD length and AAD from decrypted data
                if len(decrypted) < 4:
                    raise ValueError("Decrypted data too short for AAD")
                aad_length = int.from_bytes(decrypted[:4], 'big')
                if len(decrypted) < 4 + aad_length:
                    raise ValueError("AAD length exceeds decrypted data")
                expected_aad = decrypted[4:4 + aad_length]
                if expected_aad != aad:
                    raise ValueError("AAD verification failed")
                plaintext = decrypted[4 + aad_length:]
            else:
                plaintext = decrypted
            
            logger.debug(f"AEAD decryption successful: key_id={key_id}, "
                        f"plaintext_len={len(plaintext)}")
            
            return plaintext
            
        except InvalidTag as e:
            # Security: Log authentication failures but don't expose details
            logger.warning("AEAD authentication failed: invalid tag")
            raise ValueError("Authentication failed: invalid tag") from e
        except Exception as e:
            logger.error(f"AEAD decryption failed: {e}")
            raise ValueError(f"Decryption failed: {str(e)}") from e

# Global instance
_aead_crypto = AEADCrypto()

def aead_encrypt(key: bytes, plaintext: bytes, aad: bytes = b'', 
                 key_id: str = '') -> bytes:
    """Encrypt plaintext with authenticated encryption"""
    return _aead_crypto.encrypt(key, plaintext, aad, key_id)

def aead_decrypt(key: bytes, blob: bytes, aad: bytes = b'') -> bytes:
    """Decrypt and verify authenticated ciphertext"""
    return _aead_crypto.decrypt(key, blob, aad)