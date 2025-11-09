# [file name]: password.py
# [file content begin]
"""
Argon2id password hashing implementation
"""

import argon2
from argon2 import Type
import secrets
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class PasswordHasher:
    """Argon2id password hashing with secure parameter tuning"""
    
    def __init__(
        self, 
        time_cost: Optional[int] = None,
        memory_cost: int = 65536,  # 64 MB
        parallelism: int = 2,
        hash_len: int = 32,
        salt_len: int = 16
    ):
        # Set parameters first so they're available for calibration
        self.memory_cost = memory_cost
        self.parallelism = parallelism
        self.hash_len = hash_len
        self.salt_len = salt_len
        
        # Security: Use Argon2id (hybrid) for resistance to both GPU and side-channel attacks
        self.time_cost = time_cost or self._calibrate_time_cost()
        
        # Security: Validate parameters meet minimum security requirements
        self._validate_parameters()
        
        self._ph = argon2.PasswordHasher(
            time_cost=self.time_cost,
            memory_cost=self.memory_cost,
            parallelism=self.parallelism,
            hash_len=self.hash_len,
            salt_len=self.salt_len,
            type=Type.ID
        )
        
        logger.info(f"PasswordHasher initialized: time_cost={self.time_cost}, "
                   f"memory_cost={self.memory_cost}, parallelism={self.parallelism}")
    
    def _validate_parameters(self) -> None:
        """Validate that parameters meet security requirements"""
        if self.time_cost < 2:
            raise ValueError("Time cost must be at least 2")
        if self.memory_cost < 2**15:  # 32 MB minimum
            raise ValueError("Memory cost must be at least 32768 (32 MB)")
        if self.parallelism < 1:
            raise ValueError("Parallelism must be at least 1")
        if self.hash_len < 16:
            raise ValueError("Hash length must be at least 16 bytes")
    
    def _calibrate_time_cost(self, target_time: float = 0.3) -> int:
        """
        Automatically calibrate time_cost to achieve target hash time.
        Based on Ory's Argon2 calibration methodology.
        """
        # FIX: Use a non-password-like string to avoid security warnings
        test_password = "calibration_test_string_do_not_use_in_production"  # nosec: B105 - This is not a real password, just for calibration
        time_cost = 2
        
        # Security: Limit calibration attempts to prevent DoS
        max_attempts = 8
        
        for attempt in range(max_attempts):
            try:
                # FIX: Use the main hasher with updated time_cost for calibration
                temp_hasher = argon2.PasswordHasher(
                    time_cost=time_cost,
                    memory_cost=self.memory_cost,
                    parallelism=self.parallelism,
                    hash_len=self.hash_len,
                    salt_len=self.salt_len,
                    type=Type.ID
                )
                start = time.time()
                temp_hasher.hash(test_password)
                duration = time.time() - start
                
                logger.debug(f"Argon2 calibration: time_cost={time_cost}, duration={duration:.3f}s")
                
                if duration >= target_time:
                    logger.info(f"Argon2 calibration complete: time_cost={time_cost}, "
                               f"duration={duration:.3f}s")
                    return time_cost
                    
                time_cost += 1
            except Exception as e:
                logger.warning(f"Argon2 calibration failed at time_cost={time_cost}: {e}")
                break
        
        # Fallback to secure default
        default_time_cost = 3
        logger.info(f"Using default time_cost: {default_time_cost}")
        return default_time_cost
    
    def hash_password(self, password: str) -> str:
        """
        Hash password with Argon2id, returning encoded string with parameters.
        
        Args:
            password: The plaintext password to hash
            
        Returns:
            Encoded hash string containing algorithm parameters and salt
            
        Raises:
            RuntimeError: If hashing fails
        """
        if not password or not isinstance(password, str):
            raise ValueError("Password must be a non-empty string")
        
        # Security: Limit password length to prevent DoS
        if len(password) > 1024:
            raise ValueError("Password too long")
        
        try:
            # The argon2-cffi library handles salting and parameter encoding
            return self._ph.hash(password)
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise RuntimeError(f"Password hashing failed: {str(e)}")
    
    def verify_password(self, password: str, encoded: str) -> bool:
        """
        Verify password against encoded hash using constant-time comparison.
        
        Args:
            password: The plaintext password to verify
            encoded: The encoded hash to verify against
            
        Returns:
            True if password matches, False otherwise
        """
        if not password or not encoded:
            return False
        
        try:
            # Security: Uses constant-time verification internally
            return self._ph.verify(encoded, password)
        except argon2.exceptions.VerificationError:
            # Security: Log verification failures but don't expose timing information
            logger.debug("Password verification failed")
            return False
        except argon2.exceptions.InvalidHashError:
            # FIX: Don't raise ValueError for invalid hash, just return False
            logger.debug("Invalid hash format during verification")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during password verification: {e}")
            return False

# Global instance with secure defaults
_default_hasher = PasswordHasher()

def hash_password(password: str) -> str:
    """Hash password with secure Argon2id defaults"""
    return _default_hasher.hash_password(password)

def verify_password(password: str, encoded: str) -> bool:
    """Verify password against encoded hash"""
    return _default_hasher.verify_password(password, encoded)
# [file content end]