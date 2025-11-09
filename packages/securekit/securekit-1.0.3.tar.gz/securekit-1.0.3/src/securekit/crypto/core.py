# [file name]: core.py
# [file content begin]
"""
Core cryptographic primitives: HKDF, Ed25519, secure RNG
"""

import os
import hmac
import hashlib
import logging
from typing import Tuple, Optional
import nacl.bindings
import nacl.utils
import nacl.exceptions  # FIX: Add missing import

logger = logging.getLogger(__name__)

def hkdf_derive(salt: bytes, ikm: bytes, info: bytes, length: int) -> bytes:
    """
    Derive key material using HKDF (RFC 5869) with SHA-256.
    
    Args:
        salt: Optional salt value (non-secret)
        ikm: Input keying material
        info: Context and application specific information
        length: Length of output keying material in bytes
        
    Returns:
        Derived key material
    """
    # Security: Use HMAC-based extract-then-expand as per RFC 5869
    try:
        # Extract
        if not salt:
            salt = b'\x00' * 32  # Default salt of zeros
        
        prk = hmac.new(salt, ikm, hashlib.sha256).digest()
        
        # Expand
        n = (length + 31) // 32  # Number of blocks
        okm = b''
        t = b''
        
        for i in range(1, n + 1):
            t = hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest()
            okm += t
        
        return okm[:length]
        
    except Exception as e:
        logger.error(f"HKDF derivation failed: {e}")
        raise RuntimeError(f"HKDF derivation failed: {str(e)}")

def ed25519_keypair() -> Tuple[bytes, bytes]:
    """
    Generate a new Ed25519 key pair.
    
    Returns:
        Tuple of (private_key, public_key)
    """
    try:
        # Security: Use libsodium for proven Ed25519 implementation
        # FIX: crypto_sign_keypair returns (public_key, private_key)
        public_key, private_key = nacl.bindings.crypto_sign_keypair()
        return private_key, public_key
    except Exception as e:
        logger.error(f"Ed25519 keypair generation failed: {e}")
        raise RuntimeError(f"Keypair generation failed: {str(e)}")

def ed25519_sign(private_key: bytes, message: bytes) -> bytes:
    """
    Sign a message with Ed25519 private key.
    
    Args:
        private_key: 64-byte private key
        message: Message to sign
        
    Returns:
        Signature
        
    Raises:
        ValueError: If private key is not 64 bytes
    """
    # FIX: Don't catch ValueError - let it propagate for the test
    if len(private_key) != 64:
        raise ValueError("Private key must be 64 bytes")
    
    try:
        # Use crypto_sign which returns (signature + message), then extract signature
        signed_message = nacl.bindings.crypto_sign(message, private_key)
        # The signature is the first 64 bytes
        return signed_message[:64]
    except Exception as e:
        logger.error(f"Ed25519 signing failed: {e}")
        raise RuntimeError(f"Signing failed: {str(e)}") from e

def ed25519_verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """
    Verify Ed25519 signature.
    
    Args:
        public_key: 32-byte public key
        message: Original message
        signature: Signature to verify
        
    Returns:
        True if signature is valid
    """
    if len(public_key) != 32:
        logger.debug("Ed25519 verification failed: invalid public key size")
        return False
    
    try:
        # Security: Uses constant-time verification
        # Reconstruct signed message format for verification
        signed_message = signature + message
        nacl.bindings.crypto_sign_open(signed_message, public_key)
        return True
    except nacl.exceptions.BadSignatureError:
        logger.debug("Ed25519 signature verification failed")
        return False
    except Exception as e:
        logger.error(f"Ed25519 verification error: {e}")
        return False

def secure_random(n: int) -> bytes:
    """
    Generate cryptographically secure random bytes.
    
    Args:
        n: Number of random bytes to generate
        
    Returns:
        Random bytes
    """
    try:
        # Security: Use OS CSPRNG (urandom)
        return os.urandom(n)
    except Exception as e:
        logger.error(f"Secure random generation failed: {e}")
        raise RuntimeError(f"Random generation failed: {str(e)}")

def constant_time_compare(a: bytes, b: bytes) -> bool:
    """
    Compare two bytes in constant time to prevent timing attacks.
    
    Args:
        a: First byte string
        b: Second byte string
        
    Returns:
        True if equal
    """
    # Security: Use hmac.compare_digest for constant-time comparison
    return hmac.compare_digest(a, b)
# [file content end]