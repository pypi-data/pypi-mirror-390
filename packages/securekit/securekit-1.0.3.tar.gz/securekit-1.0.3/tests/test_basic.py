"""
Basic functionality tests for PyPI verification
"""

import pytest
import os
from securekit.crypto.password import hash_password, verify_password
from securekit.crypto.aead import aead_encrypt, aead_decrypt
from securekit.crypto.core import (
    hkdf_derive, 
    ed25519_keypair,
    ed25519_sign, 
    ed25519_verify,
    secure_random,
    constant_time_compare
)
from securekit import __version__

def test_version():
    assert __version__ == "1.0.3"

def test_imports():
    # Test that main modules can be imported
    from securekit.crypto import hash_password, verify_password
    from securekit.kms import LocalKeyManager
    assert callable(hash_password)
    assert callable(verify_password)


class TestBasicFunctionality:
    """Basic tests that should always pass"""
    
    def test_password_hashing(self):
        """Test Argon2id password hashing"""
        password = "SecurePassword123!"
        hashed = hash_password(password)
        assert verify_password(password, hashed) == True
        assert verify_password("WrongPassword", hashed) == False
    
    def test_aead_encryption(self):
        """Test authenticated encryption"""
        key = os.urandom(32)
        plaintext = b"Test secret message"
        aad = b"additional data"
        
        ciphertext = aead_encrypt(key, plaintext, aad)
        decrypted = aead_decrypt(key, ciphertext, aad)
        
        assert decrypted == plaintext
    
    def test_ed25519_signatures(self):
        """Test Ed25519 signing and verification"""
        private_key, public_key = ed25519_keypair()
        message = b"Test message for signing"
        
        signature = ed25519_sign(private_key, message)
        assert ed25519_verify(public_key, message, signature) == True
        assert ed25519_verify(public_key, b"Tampered", signature) == False
    
    def test_secure_random(self):
        """Test secure random generation"""
        r1 = secure_random(32)
        r2 = secure_random(32)
        assert len(r1) == 32
        assert len(r2) == 32
        assert r1 != r2
    
    def test_hkdf(self):
        """Test HKDF key derivation"""
        salt = b"test_salt"
        ikm = b"test_key_material"
        info = b"test_context"
        
        derived = hkdf_derive(salt, ikm, info, 32)
        assert len(derived) == 32
        
        # Same inputs should produce same output
        derived2 = hkdf_derive(salt, ikm, info, 32)
        assert derived == derived2
    
    def test_constant_time_compare(self):
        """Test constant-time comparison"""
        a = b"test_data"
        b = b"test_data"
        c = b"different"
        
        assert constant_time_compare(a, b) == True
        assert constant_time_compare(a, c) == False
