#!/usr/bin/env python3
"""
Production Security Configuration Fix Script
Run this to generate secure production keys
"""

import secrets
import os
from pathlib import Path

def generate_secure_keys():
    """Generate secure production keys"""
    
    # Generate secure JWT secret (64 characters)
    jwt_secret = secrets.token_urlsafe(48)  # 64 chars when base64 encoded
    
    # Generate secure database password
    db_password = secrets.token_urlsafe(32)
    
    print("🔐 Generated Secure Production Keys:")
    print("=" * 50)
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print(f"POSTGRES_PASSWORD={db_password}")
    print("=" * 50)
    
    # Update .env.production file
    env_file = Path(".env.production")
    if env_file.exists():
        content = env_file.read_text()
        
        # Replace placeholder values
        content = content.replace(
            "JWT_SECRET_KEY=production_jwt_secret_change_me",
            f"JWT_SECRET_KEY={jwt_secret}"
        )
        content = content.replace(
            "POSTGRES_PASSWORD=production_postgres_password_change_me",
            f"POSTGRES_PASSWORD={db_password}"
        )
        
        env_file.write_text(content)
        print("✅ Updated .env.production with secure keys")
    
    print("\n🚨 MANUAL STEPS REQUIRED:")
    print("1. Setup Firebase Service Account:")
    print("   - Go to Firebase Console → mydoc-e3824 project")
    print("   - Project Settings → Service Accounts")
    print("   - Generate new private key")
    print("   - Replace FIREBASE_PRIVATE_KEY in .env.production")
    
    print("\n2. Setup Production Database:")
    print("   - Create PostgreSQL database")
    print(f"   - Use password: {db_password}")
    print("   - Update DATABASE_URL in .env.production")

if __name__ == "__main__":
    generate_secure_keys()