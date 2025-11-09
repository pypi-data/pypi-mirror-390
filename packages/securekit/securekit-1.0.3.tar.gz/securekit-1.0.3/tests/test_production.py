# [file name]: tests/test_production.py
"""
Production test suite for SecureKit v1.0.1
Only tests core functionality - no framework integrations
"""

import pytest
import os
import tempfile
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

class TestProductionCrypto:
    """Production cryptography tests"""
    
    def test_password_hashing_production(self):
        """Test Argon2id in production scenario"""
        passwords = [
            "StrongPassword123!",
            "Another$ecureP@ss1",
            "Test123!@#",
        ]
        
        for pwd in passwords:
            hashed = hash_password(pwd)
            assert verify_password(pwd, hashed) == True
            assert verify_password("WrongPassword", hashed) == False
    
    def test_aead_encryption_production(self):
        """Test AEAD with production-like data"""
        test_cases = [
            (b"User session data", b"session_123"),
            (b"API key: sk_test_123456", b"user_456"),
            (b"Credit card data", b"payment_789"),
            (b"", b"empty_data"),  # Empty plaintext
        ]
        
        key = secure_random(32)
        
        for plaintext, aad in test_cases:
            ciphertext = aead_encrypt(key, plaintext, aad)
            decrypted = aead_decrypt(key, ciphertext, aad)
            assert decrypted == plaintext
    
    def test_ed25519_production(self):
        """Test Ed25519 with production scenarios"""
        # Generate multiple keypairs
        keypairs = [ed25519_keypair() for _ in range(3)]
        
        messages = [
            b"API request signature",
            b"JWT token payload", 
            b"Transaction data",
        ]
        
        for (priv, pub), msg in zip(keypairs, messages):
            signature = ed25519_sign(priv, msg)
            assert ed25519_verify(pub, msg, signature) == True
            
            # Verify tampering protection
            tampered_msg = msg + b"tampered"
            assert ed25519_verify(pub, tampered_msg, signature) == False

class TestProductionKMS:
    """Production KMS tests"""
    
    @pytest.fixture
    def production_keystore(self):
        """Production-like keystore"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            keystore_path = f.name
        yield keystore_path
        # Cleanup
        if os.path.exists(keystore_path):
            os.unlink(keystore_path)
        master_key_path = keystore_path + ".master"
        if os.path.exists(master_key_path):
            os.unlink(master_key_path)
    
    def test_kms_production_workflow(self, production_keystore):
        """Complete production KMS workflow"""
        km = LocalKeyManager(production_keystore)
        
        # Generate multiple keys for different purposes
        key_ids = {
            'user_encryption': km.generate_key("user_data_encryption"),
            'session_encryption': km.generate_key("session_encryption"), 
            'api_encryption': km.generate_key("api_key_encryption"),
        }
        
        # Test each key
        for purpose, key_id in key_ids.items():
            key = km.get_key(key_id)
            assert len(key) == 32
            
            # Encrypt production-like data
            test_data = f"Production data for {purpose}".encode()
            encrypted = aead_encrypt(key, test_data)
            decrypted = aead_decrypt(key, encrypted)
            assert decrypted == test_data
        
        # Verify key listing
        keys = km.list_keys()
        assert len(keys) == 3
        assert all(k['purpose'] in ['user_data_encryption', 'session_encryption', 'api_key_encryption'] 
                  for k in keys)
    
    def test_key_rotation_production(self, production_keystore):
        """Production key rotation scenario"""
        km = LocalKeyManager(production_keystore)
        
        # Create initial key
        key_id = km.generate_key("database_encryption")
        original_key = km.get_key(key_id)
        
        # Simulate production data encrypted with old key
        sensitive_data = b"Production database records"
        encrypted_data = aead_encrypt(original_key, sensitive_data)
        
        # Rotate key (as would happen in production)
        new_key_id = km.rotate_key(key_id)
        new_key = km.get_key(new_key_id)
        
        # Verify keys are different
        assert original_key != new_key
        assert key_id != new_key_id
        
        # Old data should still be decryptable with old key logic
        # (In real production, you'd maintain access to old keys for data migration)
        decrypted_with_old = aead_decrypt(original_key, encrypted_data)
        assert decrypted_with_old == sensitive_data
        
        # New data encrypted with new key
        new_data = b"New database records"
        new_encrypted = aead_encrypt(new_key, new_data)
        decrypted_with_new = aead_decrypt(new_key, new_encrypted)
        assert decrypted_with_new == new_data

def test_production_readiness():
    """Final production readiness verification"""
    print("🧪 Running production readiness tests...")
    
    # Test core crypto
    pwd = "ProductionPassword123!"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed)
    
    # Test encryption
    key = secure_random(32)
    data = b"Production-grade sensitive data"
    encrypted = aead_encrypt(key, data)
    decrypted = aead_decrypt(key, encrypted)
    assert decrypted == data
    
    # Test KMS integration
    with tempfile.NamedTemporaryFile(delete=False) as f:
        keystore_path = f.name
    
    try:
        km = LocalKeyManager(keystore_path)
        key_id = km.generate_key("production_encryption")
        kms_key = km.get_key(key_id)
        
        # Encrypt production data with KMS key
        prod_data = b"Customer PII data"
        encrypted_prod = aead_encrypt(kms_key, prod_data)
        decrypted_prod = aead_decrypt(kms_key, encrypted_prod)
        assert decrypted_prod == prod_data
        
        print("✅ PRODUCTION READY: All tests passed!")
        print("🚀 SecureKit v1.0.1 is ready for production deployment!")
        
    finally:
        if os.path.exists(keystore_path):
            os.unlink(keystore_path)
        master_path = keystore_path + '.master'
        if os.path.exists(master_path):
            os.unlink(master_path)