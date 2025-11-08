# [file name]: flask.py
# [file content begin]
"""
Flask adapter for securekit
"""

import base64
import logging
from typing import List, Callable, Any
from flask import current_app, jsonify

logger = logging.getLogger(__name__)

def register_securekit(app, key_manager):
    """
    Register securekit with Flask application.
    
    Args:
        app: Flask application instance
        key_manager: Key manager instance
    """
    app.extensions['securekit'] = {
        'key_manager': key_manager
    }
    logger.info("SecureKit registered with Flask application")

def get_key_manager():
    """Get key manager from Flask application context"""
    return current_app.extensions['securekit']['key_manager']

def get_key_id_by_purpose(purpose: str) -> str:
    """
    Get the actual key ID for a given purpose.
    
    Args:
        purpose: Key purpose (e.g., 'user_data', 'session_data')
        
    Returns:
        Actual key ID
    """
    # Check if we have a mapping in app config
    key_mapping = current_app.config.get('SECUREKIT_KEYS', {})
    if purpose in key_mapping and key_mapping[purpose]:
        return key_mapping[purpose]
    
    # Fallback: try to find a key with matching purpose
    key_manager = get_key_manager()
    keys = key_manager.list_keys()
    
    for key_info in keys:
        if key_info.get('purpose') == purpose:
            return key_info['key_id']
    
    # If no key found, create one
    new_key_id = key_manager.generate_key(purpose, {"purpose": f"{purpose}_encryption"})
    # Update the mapping
    if 'SECUREKIT_KEYS' not in current_app.config:
        current_app.config['SECUREKIT_KEYS'] = {}
    current_app.config['SECUREKIT_KEYS'][purpose] = new_key_id
    
    return new_key_id

def encrypt_fields(fields: List[str], key_purpose: str = 'user_data'):
    """
    Decorator to encrypt specified fields in JSON responses.
    
    Args:
        fields: List of field names to encrypt
        key_purpose: Key purpose for encryption (e.g., 'user_data', 'session_data')
    """
    def decorator(f: Callable) -> Callable:
        def wrapped(*args, **kwargs):
            try:
                # Get original response
                response = f(*args, **kwargs)
                
                # Only process dictionary responses
                if not isinstance(response, dict):
                    return response
                
                # Get key manager
                key_manager = get_key_manager()
                
                # Get the actual key ID for the purpose
                key_id = get_key_id_by_purpose(key_purpose)
                
                # Get encryption key
                key = key_manager.get_key(key_id)
                
                # Encrypt specified fields
                from securekit.crypto.aead import aead_encrypt
                for field in fields:
                    if field in response and response[field]:
                        # Convert to bytes if string
                        if isinstance(response[field], str):
                            plaintext = response[field].encode('utf-8')
                        else:
                            plaintext = str(response[field]).encode('utf-8')
                        
                        # Encrypt and base64 encode
                        encrypted = aead_encrypt(key, plaintext, key_id=key_id)
                        response[field] = base64.b64encode(encrypted).decode('utf-8')
                
                return response
                
            except Exception as e:
                logger.error(f"Field encryption failed: {e}")
                # Return original response if encryption fails
                return f(*args, **kwargs)
        
        return wrapped
    return decorator
# [file content end]