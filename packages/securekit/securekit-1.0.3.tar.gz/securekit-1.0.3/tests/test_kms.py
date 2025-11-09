# [file name]: tests/test_kms.py
# [file content begin]
"""
Tests for Key Management System implementations
"""

import pytest
import os
import tempfile
import json
from unittest.mock import Mock, patch

from securekit.kms.local import LocalKeyManager
from securekit.kms.aws import AWSKeyManager
from securekit.kms.vault import VaultKeyManager
from securekit.crypto.aead import aead_encrypt, aead_decrypt

class TestLocalKeyManager:
    """Test local file-based key manager"""
    
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
        
        # Old key should be marked as retired (check with include_retired=True)
        keys = km.list_keys(include_retired=True)
        old_key_info = [k for k in keys if k['key_id'] == key_id][0]
        assert old_key_info['retired'] == True
        assert old_key_info['replaced_by'] == new_key_id
        assert 'retired_at' in old_key_info
        
        # Old key should NOT appear in default list (without retired keys)
        active_keys = km.list_keys()
        old_key_in_active = [k for k in active_keys if k['key_id'] == key_id]
        assert len(old_key_in_active) == 0
        
        # New key should appear in active list
        new_key_in_active = [k for k in active_keys if k['key_id'] == new_key_id]
        assert len(new_key_in_active) == 1
    
    def test_key_not_found(self, temp_keystore):
        km = LocalKeyManager(temp_keystore)
        
        with pytest.raises(KeyError):
            km.get_key("nonexistent_key")
    
    def test_health_check(self, temp_keystore):
        km = LocalKeyManager(temp_keystore)
        
        health = km.health_check()
        assert health['status'] == 'healthy'
        assert 'keys_count' in health

class TestAWSKeyManager:
    """Test AWS KMS adapter"""
    
    @pytest.fixture
    def mock_boto3(self):
        # FIX: Mock the import inside the method, not at module level
        with patch('securekit.kms.aws.boto3') as mock_boto3:
            mock_client = Mock()
            mock_session = Mock()
            mock_session.client.return_value = mock_client
            mock_boto3.Session.return_value = mock_session
            
            # Mock KMS responses
            mock_client.create_key.return_value = {
                'KeyMetadata': {'KeyId': 'test-key-id'}
            }
            mock_client.encrypt.return_value = {
                'CiphertextBlob': b'wrapped_key_data'
            }
            mock_client.decrypt.return_value = {
                'Plaintext': b'original_key_data'
            }
            mock_client.list_keys.return_value = {
                'Keys': [{'KeyId': 'key1', 'KeyArn': 'arn:aws:kms:us-east-1:123456789012:key/key1'}]
            }
            
            yield mock_client
    
    def test_generate_key(self, mock_boto3):
        # FIX: Patch the _get_client method to avoid import issues
        with patch.object(AWSKeyManager, '_get_client') as mock_get_client:
            mock_get_client.return_value = mock_boto3
            km = AWSKeyManager(region='us-east-1')
            key_id = km.generate_key("encryption")
            
            assert key_id == 'test-key-id'
            mock_boto3.create_key.assert_called_once()
    
    def test_wrap_unwrap_key(self, mock_boto3):
        with patch.object(AWSKeyManager, '_get_client') as mock_get_client:
            mock_get_client.return_value = mock_boto3
            km = AWSKeyManager(region='us-east-1')
            
            key_to_wrap = b"test_key_data"
            wrapped = km.wrap_key(key_to_wrap, "kek-id")
            
            assert wrapped == b'wrapped_key_data'
            mock_boto3.encrypt.assert_called_once_with(
                KeyId='kek-id',
                Plaintext=key_to_wrap
            )
            
            unwrapped = km.unwrap_key(wrapped, "kek-id")
            assert unwrapped == b'original_key_data'
            mock_boto3.decrypt.assert_called_once_with(
                KeyId='kek-id',
                CiphertextBlob=wrapped
            )
    
    def test_key_rotation(self, mock_boto3):
        with patch.object(AWSKeyManager, '_get_client') as mock_get_client:
            mock_get_client.return_value = mock_boto3
            km = AWSKeyManager(region='us-east-1')
            
            key_id = km.rotate_key("test-key")
            
            assert key_id == "test-key"
            mock_boto3.enable_key_rotation.assert_called_once_with(KeyId="test-key")
    
    def test_list_keys(self, mock_boto3):
        with patch.object(AWSKeyManager, '_get_client') as mock_get_client:
            mock_get_client.return_value = mock_boto3
            km = AWSKeyManager(region='us-east-1')
            
            keys = km.list_keys()
            
            assert len(keys) == 1
            assert keys[0]['key_id'] == 'key1'
            mock_boto3.list_keys.assert_called_once()

class TestVaultKeyManager:
    """Test HashiCorp Vault adapter"""
    
    def test_generate_key(self):
        """Test Vault key generation - skip if hvac not available"""
        import os
        # Set testing environment variable to bypass HVAC check
        os.environ['SECUREKIT_TESTING'] = 'true'
        
        try:
            # Mock hvac at the module level where it's used
            with patch('securekit.kms.vault.hvac') as mock_hvac:
                mock_client = Mock()
                mock_client.is_authenticated.return_value = True
                mock_hvac.Client.return_value = mock_client
                
                # Mock transit responses
                mock_client.secrets.transit.create_key.return_value = None
                
                km = VaultKeyManager(url="http://localhost:8200", token="test-token")
                key_id = km.generate_key("encryption")
                
                # Just check it returns a string (time will be real)
                assert key_id.startswith("securekit-encryption-")
                mock_client.secrets.transit.create_key.assert_called_once()
        finally:
            # Clean up environment variable
            if 'SECUREKIT_TESTING' in os.environ:
                del os.environ['SECUREKIT_TESTING']
    
    def test_wrap_unwrap_key(self):
        """Test Vault key wrapping - skip if hvac not available"""
        import os
        os.environ['SECUREKIT_TESTING'] = 'true'
        
        try:
            with patch('securekit.kms.vault.hvac') as mock_hvac:
                mock_client = Mock()
                mock_client.is_authenticated.return_value = True
                mock_hvac.Client.return_value = mock_client
                
                # Mock transit responses
                mock_client.secrets.transit.encrypt_data.return_value = {
                    'data': {'ciphertext': 'vault:wrapped_data'}
                }
                mock_client.secrets.transit.decrypt_data.return_value = {
                    'data': {'plaintext': 'b3JpZ2luYWxfa2V5X2RhdGE='}  # base64 for 'original_key_data'
                }
                
                km = VaultKeyManager(url="http://localhost:8200", token="test-token")
                
                import base64
                key_to_wrap = b"test_key_data"
                wrapped = km.wrap_key(key_to_wrap, "kek-id")
                
                assert wrapped == b'vault:wrapped_data'
                mock_client.secrets.transit.encrypt_data.assert_called_once_with(
                    name='kek-id',
                    plaintext=base64.b64encode(key_to_wrap).decode('utf-8')
                )
                
                unwrapped = km.unwrap_key(b'vault:wrapped_data', "kek-id")
                assert unwrapped == b'original_key_data'
                mock_client.secrets.transit.decrypt_data.assert_called_once_with(
                    name='kek-id',
                    ciphertext='vault:wrapped_data'
                )
        finally:
            if 'SECUREKIT_TESTING' in os.environ:
                del os.environ['SECUREKIT_TESTING']
    
    def test_list_keys(self):
        """Test Vault key listing - skip if hvac not available"""
        import os
        os.environ['SECUREKIT_TESTING'] = 'true'
        
        try:
            with patch('securekit.kms.vault.hvac') as mock_hvac:
                mock_client = Mock()
                mock_client.is_authenticated.return_value = True
                mock_hvac.Client.return_value = mock_client
                
                mock_client.secrets.transit.list_keys.return_value = {
                    'data': {'keys': ['key1', 'key2']}
                }
                
                km = VaultKeyManager(url="http://localhost:8200", token="test-token")
                
                keys = km.list_keys()
                
                assert len(keys) == 2
                assert keys[0]['key_id'] == 'key1'
                mock_client.secrets.transit.list_keys.assert_called_once()
        finally:
            if 'SECUREKIT_TESTING' in os.environ:
                del os.environ['SECUREKIT_TESTING']

class TestCrossKMSCompatibility:
    """Test compatibility between different KMS implementations"""
    
    @pytest.fixture
    def local_km(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            keystore_path = f.name
        
        km = LocalKeyManager(keystore_path)
        yield km
        
        # Cleanup
        if os.path.exists(keystore_path):
            os.unlink(keystore_path)
        master_key_path = keystore_path + ".master"
        if os.path.exists(master_key_path):
            os.unlink(master_key_path)
    
    def test_encryption_compatibility(self, local_km):
        """Test that keys from one KMS can be used for encryption"""
        key_id = local_km.generate_key("compatibility_test")
        key = local_km.get_key(key_id)
        
        # Use key for AEAD encryption
        plaintext = b"Test data for encryption"
        ciphertext = aead_encrypt(key, plaintext, key_id=key_id)
        
        # Should be able to decrypt with same key
        decrypted = aead_decrypt(key, ciphertext)
        assert decrypted == plaintext
# [file content end]