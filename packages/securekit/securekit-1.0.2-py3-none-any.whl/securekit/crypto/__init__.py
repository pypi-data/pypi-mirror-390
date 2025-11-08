"""
Cryptography primitives with safe defaults
"""

from securekit.crypto.password import hash_password, verify_password
from securekit.crypto.aead import aead_encrypt, aead_decrypt
from securekit.crypto.core import (
    hkdf_derive,
    ed25519_keypair,
    ed25519_sign,
    ed25519_verify,
    secure_random,
    constant_time_compare,
)

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
    "constant_time_compare",
]