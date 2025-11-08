"""
Core functionality tests only - no framework integrations
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
from securekit.kms.local import LocalKeyManager
import tempfile

class TestCoreCrypto:
    """Test core cryptographic functionality"""
    
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

class TestLocalKMS:
    """Test local key management system"""
    
    @pytest.fixture
    def temp_keystore(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            keystore_path = f.name
        yield keystore_path
        # Cleanup
        if os.path.exists(keystore_path):
            os.unlink(keystore_path)
        master_key_path = keystore_path + ".master"
        if os.path.exists(master_key_path):
            os.unlink(master_key_path)
    
    def test_key_lifecycle(self, temp_keystore):
        km = LocalKeyManager(temp_keystore)
        
        # Generate key
        key_id = km.generate_key("encryption", {"app": "test"})
        assert key_id is not None
        
        # Get key
        key = km.get_key(key_id)
        assert len(key) == 32  # 256-bit key
        
        # List keys
        keys = km.list_keys()
        assert len(keys) == 1
        assert keys[0]['key_id'] == key_id
        assert keys[0]['purpose'] == "encryption"
    
    def test_key_wrapping(self, temp_keystore):
        km = LocalKeyManager(temp_keystore)
        
        # Create KEK
        kek_id = km.generate_key("key_encryption")
        
        # Wrap a data key
        data_key = os.urandom(32)
        wrapped = km.wrap_key(data_key, kek_id)
        
        # Unwrap should return original key
        unwrapped = km.unwrap_key(wrapped, kek_id)
        assert unwrapped == data_key
    
    def test_key_rotation(self, temp_keystore):
        km = LocalKeyManager(temp_keystore)
        
        key_id = km.generate_key("test_rotation")
        original_key = km.get_key(key_id)
        
        # Rotate key
        new_key_id = km.rotate_key(key_id)
        new_key = km.get_key(new_key_id)
        
        # Keys should be different
        assert original_key != new_key
        assert key_id != new_key_id
        
        # Old key should be marked as retired
        keys = km.list_keys(include_retired=True)
        old_key_info = [k for k in keys if k['key_id'] == key_id][0]
        assert old_key_info['retired'] == True
    
    def test_encryption_with_kms_keys(self, temp_keystore):
        """Test that KMS keys work with crypto functions"""
        km = LocalKeyManager(temp_keystore)
        key_id = km.generate_key("encryption_test")
        key = km.get_key(key_id)
        
        # Use KMS key for encryption
        plaintext = b"Data encrypted with KMS key"
        ciphertext = aead_encrypt(key, plaintext, key_id=key_id)
        decrypted = aead_decrypt(key, ciphertext)
        
        assert decrypted == plaintext

def test_end_to_end_workflow():
    """Test complete workflow from password hashing to encryption"""
    # Password hashing
    password = "UserPassword123"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    
    # Key management
    with tempfile.NamedTemporaryFile(delete=False) as f:
        keystore_path = f.name
    
    try:
        km = LocalKeyManager(keystore_path)
        key_id = km.generate_key("user_data")
        key = km.get_key(key_id)
        
        # Data encryption
        user_data = b"Sensitive user information"
        encrypted = aead_encrypt(key, user_data)
        decrypted = aead_decrypt(key, encrypted)
        
        assert decrypted == user_data
        print("✅ End-to-end workflow test passed!")
        
    finally:
        # Cleanup
        if os.path.exists(keystore_path):
            os.unlink(keystore_path)
        master_key_path = keystore_path + ".master"
        if os.path.exists(master_key_path):
            os.unlink(master_key_path)
