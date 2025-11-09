"""
Example FastAPI application using SecureKit
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import os

from securekit.adapters.fastapi import securekit_dependency, SecureKitDependency
from securekit.kms.local import LocalKeyManager
from securekit.crypto.password import hash_password, verify_password

app = FastAPI(title="SecureKit FastAPI Demo", version="1.0.0")

# Initialize key manager
key_manager = LocalKeyManager("./securekit_fastapi_keystore.json")
securekit_dep = securekit_dependency(key_manager)

# Create keys for demo
key_manager.generate_key("user_data", {"purpose": "user_profile_encryption"})

# In-memory user storage (use database in production)
users_db = {}

class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    phone: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserProfile(BaseModel):
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None

async def get_current_user(authorization: str = Header(None)):
    """Dependency to get current user from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization[7:]  # Remove "Bearer " prefix
    # In real app, validate JWT token
    if token in users_db:
        return users_db[token]['username']
    else:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/register")
async def register(user: UserRegister, securekit: SecureKitDependency = Depends(securekit_dep)):
    """Register new user"""
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Hash password
    hashed_password = hash_password(user.password)
    
    # Store user (in real app, save to database)
    users_db[user.username] = {
        'username': user.username,
        'password_hash': hashed_password,
        'email': user.email,
        'phone': user.phone
    }
    
    return {"message": "User registered successfully", "username": user.username}

@app.post("/login")
async def login(login_data: UserLogin, securekit: SecureKitDependency = Depends(securekit_dep)):
    """User login"""
    user = users_db.get(login_data.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if verify_password(login_data.password, user['password_hash']):
        # In real app, generate JWT token
        token = f"demo_token_{login_data.username}"
        users_db[token] = user  # Store token for demo
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/profile")
async def get_profile(
    current_user: str = Depends(get_current_user),
    securekit: SecureKitDependency = Depends(securekit_dep)
):
    """Get user profile"""
    user = users_db.get(current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Encrypt sensitive fields
    key = key_manager.get_key("user_data")
    
    encrypted_email = None
    if user['email']:
        encrypted_email = securekit.encrypt(user['email'].encode(), "user_data")
    
    encrypted_phone = None
    if user['phone']:
        encrypted_phone = securekit.encrypt(user['phone'].encode(), "user_data")
    
    return {
        "username": user['username'],
        "email": encrypted_email.hex() if encrypted_email else None,
        "phone": encrypted_phone.hex() if encrypted_phone else None
    }

@app.get("/health")
async def health_check(securekit: SecureKitDependency = Depends(securekit_dep)):
    """Health check endpoint"""
    km_health = key_manager.health_check()
    return {
        "status": "healthy",
        "key_manager": km_health,
        "users_count": len(users_db)
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to SecureKit FastAPI Demo",
        "endpoints": {
            "register": "POST /register",
            "login": "POST /login", 
            "profile": "GET /profile (requires Authorization: Bearer <token>)",
            "health": "GET /health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting SecureKit FastAPI Demo...")
    uvicorn.run(app, host="0.0.0.0", port=8000)