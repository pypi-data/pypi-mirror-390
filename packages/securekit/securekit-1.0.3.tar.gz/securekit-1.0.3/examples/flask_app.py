# [file name]: flask_app.py
# [file content begin]
"""
Example Flask application using SecureKit
"""

import os
import time
from flask import Flask, request, jsonify, session
from securekit.adapters.flask import register_securekit, encrypt_fields
from securekit.kms.local import LocalKeyManager
from securekit.crypto.password import hash_password, verify_password
import secrets

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize key manager (use cloud KMS in production)
key_manager = LocalKeyManager("./securekit_demo_keystore.json")

# Register SecureKit with Flask
register_securekit(app, key_manager)

# Store key IDs for the demo
app.config['SECUREKIT_KEYS'] = {
    'user_data': None,
    'session_data': None
}

def ensure_keys_exist():
    """Ensure required keys exist and store their IDs"""
    keys = key_manager.list_keys()
    
    # Find or create user_data key
    user_keys = [k for k in keys if k.get('purpose') == 'user_data']
    if not user_keys:
        user_key_id = key_manager.generate_key("user_data", {"purpose": "user_profile_encryption"})
        app.config['SECUREKIT_KEYS']['user_data'] = user_key_id
        print(f"Created user_data key: {user_key_id}")
    else:
        app.config['SECUREKIT_KEYS']['user_data'] = user_keys[0]['key_id']
        print(f"Using existing user_data key: {user_keys[0]['key_id']}")
    
    # Find or create session_data key  
    session_keys = [k for k in keys if k.get('purpose') == 'session_data']
    if not session_keys:
        session_key_id = key_manager.generate_key("session_data", {"purpose": "session_encryption"})
        app.config['SECUREKIT_KEYS']['session_data'] = session_key_id
        print(f"Created session_data key: {session_key_id}")
    else:
        app.config['SECUREKIT_KEYS']['session_data'] = session_keys[0]['key_id']
        print(f"Using existing session_data key: {session_keys[0]['key_id']}")

# Ensure keys exist when app starts
with app.app_context():
    ensure_keys_exist()

@app.route('/')
def hello():
    return jsonify({
        "message": "Welcome to SecureKit Flask Demo",
        "endpoints": {
            "register": "POST /register - Create user with encrypted data",
            "login": "POST /login - User login",
            "profile": "GET /profile - Get encrypted user profile",
            "health": "GET /health - System health check"
        }
    })

@app.route('/register', methods=['POST'])
def register():
    """Register new user with encrypted profile data"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password required"}), 400
    
    # Hash password with Argon2id
    hashed_password = hash_password(data['password'])
    
    # In a real app, you'd save this to a database
    user_data = {
        'username': data['username'],
        'password_hash': hashed_password,
        'email': data.get('email', ''),
        'phone': data.get('phone', ''),
        'created_at': time.time()
    }
    
    # Store user data (in memory for demo)
    users = getattr(app, 'users', {})
    users[data['username']] = user_data
    app.users = users
    
    return jsonify({
        "message": "User registered successfully",
        "user_id": data['username']
    })

@app.route('/login', methods=['POST'])
def login():
    """User login with password verification"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password required"}), 400
    
    users = getattr(app, 'users', {})
    user = users.get(data['username'])
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Verify password with constant-time comparison
    if verify_password(data['password'], user['password_hash']):
        session['user'] = data['username']
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"error": "Invalid password"}), 401

@app.route('/profile')
@encrypt_fields(['email', 'phone'], 'user_data')
def get_profile():
    """Get user profile with encrypted sensitive fields"""
    if 'user' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    users = getattr(app, 'users', {})
    user = users.get(session['user'])
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Return user profile (email and phone will be encrypted)
    return {
        "username": user['username'],
        "email": user['email'],
        "phone": user['phone'],
        "created_at": user['created_at']
    }

@app.route('/health')
def health_check():
    """Health check endpoint"""
    km_health = key_manager.health_check()
    return jsonify({
        "status": "healthy",
        "key_manager": km_health,
        "users_count": len(getattr(app, 'users', {}))
    })

@app.route('/keys')
def list_keys():
    """List available keys (for demo only - secure in production)"""
    keys = key_manager.list_keys()
    return jsonify({"keys": keys})

@app.route('/key-info')
def key_info():
    """Show key mapping (for demo only)"""
    return jsonify({
        "key_mapping": app.config['SECUREKIT_KEYS'],
        "all_keys": key_manager.list_keys()
    })

if __name__ == '__main__':
    print("Starting SecureKit Flask Demo...")
    print("Available endpoints:")
    print("  GET  / - This help message")
    print("  POST /register - Register new user")
    print("  POST /login - User login") 
    print("  GET  /profile - Get encrypted user profile")
    print("  GET  /health - Health check")
    print("  GET  /keys - List keys (demo only)")
    print("  GET  /key-info - Key mapping (demo only)")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
# [file content end]