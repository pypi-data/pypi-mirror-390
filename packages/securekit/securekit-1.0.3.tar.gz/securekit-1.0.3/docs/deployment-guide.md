# ✅ SecureKit — Production Deployment Guide

## 🚀 Overview
SecureKit is a modular, framework-compatible security library designed to provide ultra-strong cryptography, safe key management, and enterprise-grade deployment controls.

---

## ✅ 1. Prerequisites

### ✅ System Requirements
- Python **3.8+**
- 64-bit OS
- Minimum **512MB RAM** (Argon2 uses memory heavily)

### ✅ Security Requirements
- Secure key management setup
- Isolated network for crypto operations
- Regular backup routines

---

## ✅ 2. Installation

### 📦 From PyPI
```
pip install securekit
```

### Optional Framework Integrations
```
# Flask
pip install securekit[flask]

# Django
pip install securekit[django]

# FastAPI
pip install securekit[fastapi]

# AWS KMS
pip install securekit[aws]

# HashiCorp Vault
pip install securekit[vault]
```

---

## ✅ 3. Key Management

> ⚠️ **Never use local file key storage in production**

### ✅ Recommended Key Managers
- AWS KMS
- HashiCorp Vault
- Hardware Security Modules (HSM)
- Azure Key Vault / Google Cloud KMS

### 🔁 Key Rotation Strategy
| Key Type | Rotation |
|----------|----------|
| Data Encryption Keys | Monthly |
| Key Encryption Keys | Quarterly |
| Master Keys | Annually |
| Security Incident Keys | Immediate |

---

## ✅ 4. Configuration

### ✅ Environment Variables
```
# Argon2
export SECUREKIT_ARGON2_TIME_COST=4
export SECUREKIT_ARGON2_MEMORY_COST=131072
export SECUREKIT_ARGON2_PARALLELISM=2

# Key Management
export SECUREKIT_KMS_TYPE=aws
export SECUREKIT_KEY_ROTATION_DAYS=30

# AWS KMS
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key

# HashiCorp Vault
export SECUREKIT_VAULT_URL=https://vault.example.com
export SECUREKIT_VAULT_TOKEN=your_vault_token
```

### ✅ Optional YAML Configuration
```
argon2:
  time_cost: 4
  memory_cost: 131072
  parallelism: 2

kms:
  type: aws
  aws:
    region: us-east-1
    key_id: alias/securekit-prod

logging:
  level: INFO
  audit_enabled: true
```

---

## ✅ 5. Framework Integration

### 🔹 Flask
```
from flask import Flask
from securekit.adapters.flask import register_securekit
from securekit.kms.aws import AWSKeyManager

app = Flask(__name__)
key_manager = AWSKeyManager(region='us-east-1')

register_securekit(app, key_manager)

@app.route('/secure-data')
@encrypt_fields(['email', 'ssn'])
def get_secure_data():
    return {'email': 'user@example.com', 'ssn': '123-45-6789'}
```

### 🔹 Django
```
# settings.py
SECUREKIT_KEY_MANAGER = AWSKeyManager(region='us-east-1')

# models.py
from securekit.adapters.django import EncryptedField
from django.db import models

class UserProfile(models.Model):
    social_security = EncryptedField(max_length=255)
    medical_data = EncryptedField(max_length=1024)
```
### 🔹 FastAPI
```
from fastapi import FastAPI, Depends
from securekit.adapters.fastapi import securekit_dependency, encrypt_response
from securekit.kms.aws import AWSKeyManager

app = FastAPI()
key_manager = AWSKeyManager(region='us-east-1')

@app.get("/secure-data")
@encrypt_response(['sensitive_field'])
async def get_secure_data(securekit = Depends()):
    return {'sensitive_field': 'confidential_data'}
```

---

## ✅ 6. Security Hardening

### ✅ OS Level
```
# Secure permissions
chmod 600 /path/to/securekit/config
chown root:root /path/to/securekit

# Firewall
ufw allow from 10.0.0.0/8 to any port 443
```

### ✅ App Security Suggestions
- Use HTTPS
- Rate limiting
- Apply security updates
- Follow least-privilege access

---

## ✅ 7. Monitoring & Alerting

### 🔍 Metrics to Monitor
- Cryptographic latency
- Key rotation success
- Authentication failures
- Argon2 memory usage

### 🚨 Alerts
- Failed decrypt attempts
- Rotation failures
- Odd access patterns
- Config changes

---

## ✅ 8. Backup & Recovery

### 🔐 Key Backup Strategy
1. Multi-region KMS
2. Offline backups for master keys
3. Routine recovery test

### 🔄 Sample Recovery
```
from securekit.kms.aws import AWSKeyManager
from securekit.crypto.aead import aead_decrypt

def recover_data(encrypted_data, backup_key_id):
    key_manager = AWSKeyManager()
    key = key_manager.get_key(backup_key_id)
    return aead_decrypt(key, encrypted_data)
```

---

## ✅ 9. Performance Tuning

### ⚙️ Argon2 Tiers
| Mode | time_cost | memory_cost |
|------|-----------|-------------|
| Development | 2 | 64MB |
| Production | 4 | 128MB |
| High-Security | 6 | 256MB |

### Memory Check
```
import psutil
import resource

def check_memory_limits():
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    return f"Memory limit: {soft} bytes"
```
---

## ✅ 10. Compliance & Auditing

### ✅ Example Audit Logging
```
from securekit.utils.security import audit_log

audit_log('user_login', {'user_id': 123, 'ip': '192.168.1.1'})
audit_log('key_rotation', {'key_id': 'key_123', 'status': 'success'})
```

### ✅ Checklist
- Documented key procedures
- Regular security audits
- Controlled access
- Incident plan in place

---

## ✅ 11. Troubleshooting

### ⚠️ Common Problems
| Issue | Fix |
|-------|-----|
| Memory errors | Lower Argon2 memory_cost |
| Slowness | Reduce time_cost |
| KMS errors | Check permissions & network |

### Debug Mode
```
import logging
logging.getLogger('securekit').setLevel(logging.DEBUG)
```

---

## 📞 Support
| Type | Contact |
|------|---------|
| Security | security@example.com |
| Support | support@example.com |
| Docs | https://securekit.readthedocs.io |