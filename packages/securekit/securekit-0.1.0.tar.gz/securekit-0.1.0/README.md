# SecureKit

A production-ready, highly secure cryptography library for Python applications.

## Features

- **Secure Cryptography Primitives**: Argon2id, ChaCha20-Poly1305, Ed25519, HKDF
- **Pluggable Key Management**: Local, AWS KMS, HashiCorp Vault, HSM support
- **Framework Integrations**: Flask, Django, FastAPI
- **Security by Default**: Safe defaults, constant-time operations, secure configurations
- **Production Ready**: Key rotation, audit logging, comprehensive testing

## Quick Start

### Installation

```bash
pip install securekit
```

Basic Usage

```python
from securekit.crypto.password import hash_password, verify_password
from securekit.crypto.aead import aead_encrypt, aead_decrypt

# Password hashing
hashed = hash_password("my_secure_password")
is_valid = verify_password("my_secure_password", hashed)

# Authenticated encryption
key = b'\x00' * 32  # 256-bit key
ciphertext = aead_encrypt(key, b"sensitive_data")
plaintext = aead_decrypt(key, ciphertext)
```

Documentation

· Threat Model
· Deployment Guide
· API Reference

Security

Please report security vulnerabilities to security@example.com.

License

Apache 2.0
