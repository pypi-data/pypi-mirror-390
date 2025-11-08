"""
SecureKit - Production-ready cryptography library for Python
"""

__version__ = "0.1.0"
__author__ = "SecureKit Team"
__email__ = "security@example.com"

from securekit.crypto import (
    hash_password,
    verify_password,
    aead_encrypt,
    aead_decrypt,
    hkdf_derive,
    ed25519_keypair,
    ed25519_sign,
    ed25519_verify,
    secure_random,
)
from securekit.kms import KeyManager, LocalKeyManager

__all__ = [
    "hash_password",
    "verify_password", 
    "aead_encrypt",
    "aead_decrypt",
    "hkdf_derive",
    "ed25519_keypair",
    "ed25519_sign",
    "ed25519_verify",
    "secure_random",
    "KeyManager",
    "LocalKeyManager",
]