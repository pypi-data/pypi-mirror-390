"""
Web framework adapters for securekit
"""

from securekit.adapters.flask import register_securekit, encrypt_fields
from securekit.adapters.django import SecureKitMiddleware, EncryptedField
from securekit.adapters.fastapi import securekit_dependency, encrypt_response

__all__ = [
    "register_securekit",
    "encrypt_fields", 
    "SecureKitMiddleware",
    "EncryptedField",
    "securekit_dependency",
    "encrypt_response",
]