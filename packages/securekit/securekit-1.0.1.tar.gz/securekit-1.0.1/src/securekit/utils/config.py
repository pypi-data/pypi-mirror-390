"""
Configuration management for securekit
"""

import os
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

def get_env_var(name: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get environment variable with security validation.
    
    Args:
        name: Environment variable name
        default: Default value if not found
        required: Whether the variable is required
        
    Returns:
        Environment variable value
        
    Raises:
        RuntimeError: If required variable is missing
    """
    value = os.getenv(name, default)
    
    if required and value is None:
        raise RuntimeError(f"Required environment variable not set: {name}")
    
    # Security: Log when using default values for sensitive config
    if value == default and name in _sensitive_config_names():
        logger.warning(f"Using default value for sensitive config: {name}")
    
    return value

def load_config(config_path: Optional[str] = None) -> dict:
    """
    Load configuration from file and environment.
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        Configuration dictionary
    """
    config = {
        'argon2': {
            'time_cost': int(get_env_var('SECUREKIT_ARGON2_TIME_COST', '3')),
            'memory_cost': int(get_env_var('SECUREKIT_ARGON2_MEMORY_COST', '65536')),
            'parallelism': int(get_env_var('SECUREKIT_ARGON2_PARALLELISM', '2')),
        },
        'kms': {
            'type': get_env_var('SECUREKIT_KMS_TYPE', 'local'),
            'local_path': get_env_var('SECUREKIT_LOCAL_KEYSTORE', '~/.securekit/keystore.json'),
        }
    }
    
    # Load from file if provided
    if config_path and os.path.exists(config_path):
        try:
            import yaml
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                _deep_update(config, file_config)
        except Exception as e:
            logger.warning(f"Failed to load config file {config_path}: {e}")
    
    return config

def _sensitive_config_names() -> list:
    """List of sensitive configuration variable names"""
    return [
        'SECUREKIT_MASTER_KEY',
        'SECUREKIT_VAULT_TOKEN',
        'SECUREKIT_AWS_SECRET_KEY',
    ]

def _deep_update(base: dict, update: dict):
    """Recursively update a dictionary"""
    for key, value in update.items():
        if isinstance(value, dict) and key in base and isinstance(base[key], dict):
            _deep_update(base[key], value)
        else:
            base[key] = value