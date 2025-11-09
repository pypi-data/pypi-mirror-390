"""
Security utilities for securekit
"""

import hmac
import logging
import time
from typing import Any, Dict, Optional

# Security audit logger (separate from application logger)
audit_logger = logging.getLogger('securekit.audit')

def constant_time_compare(a: bytes, b: bytes) -> bool:
    """
    Compare two bytes in constant time to prevent timing attacks.
    
    Args:
        a: First byte string
        b: Second byte string
        
    Returns:
        True if equal
    """
    return hmac.compare_digest(a, b)

def audit_log(event: str, data: Optional[Dict[str, Any]] = None, 
              user: Optional[str] = None, success: bool = True):
    """
    Log security events for auditing.
    
    Security: NEVER log secrets, keys, or sensitive data.
    
    Args:
        event: Event type (e.g., 'key_generated', 'password_verified')
        data: Additional event data (no secrets!)
        user: User identifier if available
        success: Whether the operation was successful
    """
    audit_data = {
        'timestamp': time.time(),
        'event': event,
        'user': user,
        'success': success,
        'data': data or {}
    }
    
    # Security: Sanitize data before logging
    sanitized_data = _sanitize_audit_data(audit_data)
    
    if success:
        audit_logger.info("Security event: %s", sanitized_data)
    else:
        audit_logger.warning("Security event failed: %s", sanitized_data)

def _sanitize_audit_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize audit data to remove any potentially sensitive information.
    """
    sanitized = data.copy()
    
    # Remove any fields that might contain secrets
    sensitive_keys = ['password', 'secret', 'key', 'token', 'credential']
    for key in list(sanitized.get('data', {}).keys()):
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized['data'][key] = '***REDACTED***'
    
    return sanitized