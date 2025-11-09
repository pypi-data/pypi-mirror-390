"""
Django models example using SecureKit EncryptedField
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from securekit.adapters.django import EncryptedField

class SecureUser(AbstractUser):
    """User model with encrypted PII fields"""
    
    # Regular fields
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Encrypted fields
    social_security = EncryptedField(
        max_length=255, 
        blank=True, 
        null=True,
        key_id="user_pii"
    )
    
    medical_record_number = EncryptedField(
        max_length=255,
        blank=True,
        null=True, 
        key_id="user_pii"
    )
    
    credit_card_token = EncryptedField(
        max_length=255,
        blank=True,
        null=True,
        key_id="payment_data"
    )
    
    class Meta:
        verbose_name = "Secure User"
        verbose_name_plural = "Secure Users"

class EncryptedDocument(models.Model):
    """Model for storing encrypted documents"""
    
    title = models.CharField(max_length=255)
    content = EncryptedField(
        key_id="document_encryption"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class SecureConfig(models.Model):
    """Encrypted configuration storage"""
    
    key = models.CharField(max_length=255, unique=True)
    value = EncryptedField(
        key_id="config_encryption"
    )
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.key