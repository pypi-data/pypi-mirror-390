"""
Tests for framework adapters
"""

import pytest
import json
from unittest.mock import Mock, patch
from base64 import b64encode

# Flask tests
@pytest.fixture
def flask_app():
    from flask import Flask
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def flask_client(flask_app):
    return flask_app.test_client()

class TestFlaskAdapter:
    """Test Flask adapter functionality"""
    
    def test_register_securekit(self, flask_app):
        from securekit.adapters.flask import register_securekit
        from securekit.kms.local import LocalKeyManager
        
        key_manager = Mock(spec=LocalKeyManager)
        
        register_securekit(flask_app, key_manager)
        
        assert 'securekit' in flask_app.extensions
        assert flask_app.extensions['securekit']['key_manager'] == key_manager
    
    def test_encrypt_fields_decorator(self, flask_app):
        from securekit.adapters.flask import register_securekit, encrypt_fields
        from securekit.kms.local import LocalKeyManager
        
        # Mock key manager
        key_manager = Mock(spec=LocalKeyManager)
        key_manager.get_key.return_value = b'\x00' * 32  # 256-bit zero key
        
        register_securekit(flask_app, key_manager)
        
        @flask_app.route('/test')
        @encrypt_fields(['secret_data'])
        def test_route():
            return {'secret_data': 'sensitive_value', 'public_data': 'non_sensitive'}
        
        with flask_app.test_client() as client:
            with patch('securekit.crypto.aead.aead_encrypt') as mock_encrypt:
                mock_encrypt.return_value = b'encrypted_data'
                
                response = client.get('/test')
                data = json.loads(response.data)
                
                # Secret data should be encrypted
                assert data['secret_data'] == b64encode(b'encrypted_data').decode('utf-8')
                # Public data should remain unchanged
                assert data['public_data'] == 'non_sensitive'

# Django tests
@pytest.mark.django_db
class TestDjangoAdapter:
    """Test Django adapter functionality"""
    
    def test_encrypted_field(self):
        from securekit.adapters.django import EncryptedField
        from django.db import models
        
        # Create a test model with encrypted field
        class TestModel(models.Model):
            secret = EncryptedField(key_id="test_key")
            
            class Meta:
                app_label = 'test_app'
        
        field = TestModel._meta.get_field('secret')
        
        assert isinstance(field, EncryptedField)
        assert field.key_id == "test_key"
    
    def test_encrypted_field_operations(self):
        # This would require Django model testing setup
        # Testing encryption/decryption in Django context
        pass

# FastAPI tests  
class TestFastAPIAdapter:
    """Test FastAPI adapter functionality"""
    
    def test_securekit_dependency(self):
        from securekit.adapters.fastapi import SecureKitDependency
        from securekit.kms.local import LocalKeyManager
        
        key_manager = Mock(spec=LocalKeyManager)
        dependency = SecureKitDependency(key_manager)
        
        assert dependency.key_manager == key_manager
    
    def test_encrypt_decrypt_methods(self):
        from securekit.adapters.fastapi import SecureKitDependency
        from securekit.kms.local import LocalKeyManager
        
        key_manager = Mock(spec=LocalKeyManager)
        key_manager.get_key.return_value = b'\x00' * 32
        
        dependency = SecureKitDependency(key_manager)
        
        with patch('securekit.crypto.aead.aead_encrypt') as mock_encrypt:
            mock_encrypt.return_value = b'encrypted_data'
            
            result = dependency.encrypt(b'test_data', 'test_key')
            assert result == b'encrypted_data'
        
        with patch('securekit.crypto.aead.aead_decrypt') as mock_decrypt:
            mock_decrypt.return_value = b'decrypted_data'
            
            result = dependency.decrypt(b'encrypted_data', 'test_key')
            assert result == b'decrypted_data'

class TestFrameworkCompatibility:
    """Test cross-framework compatibility"""
    
    def test_key_manager_consistency(self):
        """Test that same key manager works across all adapters"""
        from securekit.kms.local import LocalKeyManager
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            keystore_path = f.name
        
        try:
            key_manager = LocalKeyManager(keystore_path)
            key_id = key_manager.generate_key("cross_framework_test")
            
            # Key should be accessible
            key = key_manager.get_key(key_id)
            assert len(key) == 32
            
            # Key should work for encryption
            from securekit.crypto.aead import aead_encrypt, aead_decrypt
            plaintext = b"Cross-framework test data"
            ciphertext = aead_encrypt(key, plaintext, key_id=key_id)
            decrypted = aead_decrypt(key, ciphertext)
            assert decrypted == plaintext
            
        finally:
            # Cleanup
            if os.path.exists(keystore_path):
                os.unlink(keystore_path)
            master_key_path = keystore_path + ".master"
            if os.path.exists(master_key_path):
                os.unlink(master_key_path)