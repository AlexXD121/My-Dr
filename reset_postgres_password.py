#!/usr/bin/env python3
"""
PostgreSQL Password Reset Helper
Helps reset the postgres user password
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def try_windows_auth():
    """Try connecting with Windows authentication"""
    try:
        # Try Windows authentication (no password)
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="postgres",
            user="postgres"
            # No password - uses Windows auth
        )
        conn.close()
        logger.info("✅ Windows authentication works!")
        return True
    except Exception as e:
        logger.info(f"Windows auth failed: {e}")
        return False

def try_common_passwords():
    """Try common default passwords"""
    common_passwords = ["", "postgres", "admin", "password", "123456"]
    
    for password in common_passwords:
        try:
            conn = psycopg2.connect(
                host="localhost",
                port="5432",
                database="postgres",
                user="postgres",
                password=password
            )
            conn.close()
            logger.info(f"✅ Found working password: '{password}' (empty if blank)")
            return password
        except Exception:
            continue
    
    return None

def reset_password_with_psql():
    """Try to reset password using psql command"""
    logger.info("Attempting to reset password using psql...")
    
    # Try to run psql command to reset password
    reset_command = 'psql -U postgres -c "ALTER USER postgres PASSWORD \'Dhaval@191004\';"'
    
    try:
        result = os.system(reset_command)
        if result == 0:
            logger.info("✅ Password reset successful!")
            return True
        else:
            logger.error("❌ Password reset failed")
            return False
    except Exception as e:
        logger.error(f"❌ Error running psql: {e}")
        return False

def main():
    """Main function to help with password issues"""
    logger.info("🔐 PostgreSQL Password Helper")
    
    # Try Windows authentication first
    if try_windows_auth():
        logger.info("💡 Use Windows authentication - remove password from connection")
        return True
    
    # Try common passwords
    working_password = try_common_passwords()
    if working_password is not None:
        logger.info(f"💡 Update .env.production with password: '{working_password}'")
        return True
    
    # Try to reset password
    logger.info("Trying to reset password...")
    if reset_password_with_psql():
        return True
    
    logger.error("❌ Could not resolve password issue")
    logger.info("📋 Manual steps to fix:")
    logger.info("1. Open Command Prompt as Administrator")
    logger.info("2. Run: psql -U postgres")
    logger.info("3. If prompted for password, try: postgres, admin, or leave blank")
    logger.info("4. Once connected, run: ALTER USER postgres PASSWORD 'Dhaval@191004';")
    logger.info("5. Exit with: \\q")
    
    return False

if __name__ == "__main__":
    main()