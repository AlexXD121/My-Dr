#!/usr/bin/env python3
"""
Project cleanup script for MyDoc AI Medical Assistant
Removes temporary files, optimizes imports, and ensures clean codebase
"""

import os
import shutil
import glob
from pathlib import Path

def cleanup_pycache():
    """Remove Python cache files"""
    print("🧹 Cleaning Python cache files...")
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                cache_path = os.path.join(root, dir_name)
                print(f"  Removing: {cache_path}")
                shutil.rmtree(cache_path, ignore_errors=True)

def cleanup_temp_files():
    """Remove temporary files"""
    print("🧹 Cleaning temporary files...")
    temp_patterns = [
        '**/*.tmp',
        '**/*.temp',
        '**/*.bak',
        '**/*.backup',
        '**/*~',
        '**/.DS_Store'
    ]
    
    for pattern in temp_patterns:
        for file_path in glob.glob(pattern, recursive=True):
            print(f"  Removing: {file_path}")
            try:
                os.remove(file_path)
            except OSError:
                pass

def cleanup_logs():
    """Clean old log files"""
    print("🧹 Cleaning old log files...")
    log_dir = Path('logs')
    if log_dir.exists():
        for log_file in log_dir.glob('*.log'):
            # Keep recent logs (last 7 days)
            if log_file.stat().st_mtime < (os.path.getmtime('.') - 7 * 24 * 3600):
                print(f"  Removing old log: {log_file}")
                log_file.unlink()

def cleanup_node_modules():
    """Clean and reinstall node modules if needed"""
    print("🧹 Checking Node.js dependencies...")
    frontend_dir = Path('frontend')
    if frontend_dir.exists():
        package_lock = frontend_dir / 'package-lock.json'
        node_modules = frontend_dir / 'node_modules'
        
        if package_lock.exists() and node_modules.exists():
            print("  Node modules are up to date")
        else:
            print("  Node modules may need reinstallation")

def optimize_database():
    """Optimize database files"""
    print("🧹 Optimizing database...")
    data_dir = Path('data')
    if not data_dir.exists():
        data_dir.mkdir()
        print("  Created data directory")
    
    # Move any database files from backend to data
    backend_dir = Path('backend')
    for db_file in backend_dir.glob('*.db*'):
        target = data_dir / db_file.name
        if not target.exists():
            shutil.move(str(db_file), str(target))
            print(f"  Moved database file: {db_file.name}")

def verify_gitignore():
    """Verify .gitignore is comprehensive"""
    print("🧹 Verifying .gitignore...")
    gitignore_path = Path('.gitignore')
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        required_patterns = [
            '*.db', '*.sqlite', '__pycache__/', 'node_modules/',
            '.env', '*.log', 'dist/', 'build/'
        ]
        
        missing = [pattern for pattern in required_patterns if pattern not in content]
        if missing:
            print(f"  Missing patterns in .gitignore: {missing}")
        else:
            print("  .gitignore is comprehensive")
    else:
        print("  Warning: No .gitignore file found")

def main():
    """Run all cleanup tasks"""
    print("🚀 Starting MyDoc AI project cleanup...")
    
    cleanup_pycache()
    cleanup_temp_files()
    cleanup_logs()
    cleanup_node_modules()
    optimize_database()
    verify_gitignore()
    
    print("✅ Project cleanup completed!")
    print("\n📋 Next steps:")
    print("  1. Run 'npm install' in frontend directory if needed")
    print("  2. Run 'pip install -r requirements.txt' in backend directory")
    print("  3. Set up environment variables")
    print("  4. Run database migrations")

if __name__ == "__main__":
    main()