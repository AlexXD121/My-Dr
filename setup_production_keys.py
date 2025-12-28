#!/usr/bin/env python3
"""
Production Environment Setup Helper
Run this script to interactively set up your production keys
"""

import os
import json

def setup_firebase_key():
    print("\n🔥 FIREBASE SETUP")
    print("1. Go to: https://console.firebase.google.com/")
    print("2. Select your project (or create 'mydoc-production')")
    print("3. Go to Project Settings → Service Accounts")
    print("4. Click 'Generate new private key'")
    print("5. Download the JSON file")
    
    json_path = input("\nEnter path to downloaded Firebase JSON file: ").strip()
    
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                firebase_data = json.load(f)
            
            private_key = firebase_data.get('private_key', '')
            project_id = firebase_data.get('project_id', '')
            
            if private_key and project_id:
                print(f"✅ Found Firebase config for project: {project_id}")
                return private_key, project_id
            else:
                print("❌ Invalid Firebase JSON file")
                return None, None
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None, None
    else:
        print("❌ File not found")
        return None, None

def setup_sentry_dsn():
    print("\n📊 SENTRY SETUP")
    print("1. Go to: https://sentry.io/")
    print("2. Sign up or log in")
    print("3. Create new project → Python → 'mydoc-production'")
    print("4. Copy the DSN (looks like: https://abc123@o123.ingest.sentry.io/123)")
    
    dsn = input("\nPaste your Sentry DSN here: ").strip()
    
    if dsn.startswith('https://') and 'sentry.io' in dsn:
        print("✅ Valid Sentry DSN format")
        return dsn
    else:
        print("❌ Invalid DSN format")
        return None

def update_env_file(firebase_key, firebase_project, sentry_dsn):
    env_file = '.env.production'
    
    if not os.path.exists(env_file):
        print(f"❌ {env_file} not found")
        return False
    
    # Read current content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Replace placeholders
    if firebase_key:
        content = content.replace(
            'FIREBASE_PRIVATE_KEY=production_firebase_key_change_me',
            f'FIREBASE_PRIVATE_KEY="{firebase_key}"'
        )
    
    if firebase_project:
        content = content.replace(
            'FIREBASE_PROJECT_ID=mydoc-production',
            f'FIREBASE_PROJECT_ID={firebase_project}'
        )
    
    if sentry_dsn:
        content = content.replace(
            'SENTRY_DSN=https://production_sentry_dsn_change_me',
            f'SENTRY_DSN={sentry_dsn}'
        )
    
    # Write back
    with open(env_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {env_file}")
    return True

def main():
    print("🚀 My Dr AI - Production Environment Setup")
    print("=" * 50)
    
    # Setup Firebase
    firebase_key, firebase_project = setup_firebase_key()
    
    # Setup Sentry
    sentry_dsn = setup_sentry_dsn()
    
    # Update .env.production
    if firebase_key or sentry_dsn:
        print("\n📝 UPDATING .env.production")
        if update_env_file(firebase_key, firebase_project, sentry_dsn):
            print("\n🎉 Setup complete!")
            print("\nNext steps:")
            print("1. Test the configuration")
            print("2. Move to Issue #2: Database Setup")
        else:
            print("\n❌ Failed to update environment file")
    else:
        print("\n⚠️ No valid keys provided. Please try again.")

if __name__ == "__main__":
    main()