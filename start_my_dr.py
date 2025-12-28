#!/usr/bin/env python3
"""
My Dr - Startup Script
Helps initialize and start the My Dr medical assistant application
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

def print_header():
    """Print application header"""
    print("=" * 60)
    print("🩺 MY DR - AI Medical Assistant")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_node_version():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js version: {version}")
            return True
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not installed")
        return False

def setup_backend():
    """Setup backend dependencies and database"""
    print("\n🔧 Setting up backend...")
    
    # Check if backend directory exists
    if not os.path.exists('backend'):
        print("❌ Backend directory not found")
        return False
    
    os.chdir('backend')
    
    # Install Python dependencies
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Python dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False
    
    # Initialize database
    print("📊 Initializing database...")
    try:
        subprocess.run([sys.executable, 'migrations.py'], check=True, capture_output=True)
        print("✅ Database initialized")
    except subprocess.CalledProcessError as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    os.chdir('..')
    return True

def setup_frontend():
    """Setup frontend dependencies"""
    print("\n🎨 Setting up frontend...")
    
    # Check if frontend directory exists
    if not os.path.exists('frontend'):
        print("❌ Frontend directory not found")
        return False
    
    os.chdir('frontend')
    
    # Install Node.js dependencies
    print("📦 Installing Node.js dependencies...")
    try:
        subprocess.run(['npm', 'install'], check=True, capture_output=True)
        print("✅ Node.js dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Node.js dependencies: {e}")
        return False
    
    os.chdir('..')
    return True

def check_jan_ai():
    """Check if Jan AI is running"""
    print("\n🤖 Checking Jan AI connection...")
    try:
        response = requests.get('http://localhost:1337/v1/models', timeout=5)
        if response.status_code == 200:
            print("✅ Jan AI is running and accessible")
            return True
        else:
            print(f"⚠️  Jan AI responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ Jan AI is not running or not accessible")
        print("   Please start Jan AI and enable the API server on port 1337")
        return False

def start_backend():
    """Start the backend server"""
    print("\n🚀 Starting backend server...")
    
    os.chdir('backend')
    
    # Start backend in background
    try:
        process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'main:app', '--reload', '--host', '0.0.0.0', '--port', '8000'])
        print(f"✅ Backend started (PID: {process.pid})")
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Test if backend is responding
        try:
            response = requests.get('http://localhost:8000/health', timeout=5)
            if response.status_code == 200:
                print("✅ Backend is responding")
                os.chdir('..')
                return process
            else:
                print(f"⚠️  Backend responded with status {response.status_code}")
        except requests.exceptions.RequestException:
            print("❌ Backend is not responding")
        
        os.chdir('..')
        return process
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        os.chdir('..')
        return None

def start_frontend():
    """Start the frontend development server"""
    print("\n🎨 Starting frontend server...")
    
    os.chdir('frontend')
    
    # Start frontend in background
    try:
        process = subprocess.Popen(['npm', 'run', 'dev'])
        print(f"✅ Frontend started (PID: {process.pid})")
        
        # Wait a moment for server to start
        time.sleep(5)
        
        os.chdir('..')
        return process
        
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        os.chdir('..')
        return None

def print_success_message():
    """Print success message with URLs"""
    print("\n" + "=" * 60)
    print("🎉 MY DR IS READY!")
    print("=" * 60)
    print()
    print("🌐 Frontend: http://localhost:5173")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print()
    print("💡 Tips:")
    print("   • Make sure Jan AI is running for best AI responses")
    print("   • Check the connection status indicator in the app")
    print("   • Use Ctrl+C to stop the servers")
    print()
    print("🩺 Ready to help with your medical questions!")
    print("=" * 60)

def main():
    """Main startup function"""
    print_header()
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_node_version():
        print("Please install Node.js from https://nodejs.org/")
        sys.exit(1)
    
    # Setup dependencies
    if not setup_backend():
        print("❌ Backend setup failed")
        sys.exit(1)
    
    if not setup_frontend():
        print("❌ Frontend setup failed")
        sys.exit(1)
    
    # Check Jan AI (optional)
    jan_ai_running = check_jan_ai()
    if not jan_ai_running:
        print("⚠️  Jan AI is not running. AI responses may use fallback messages.")
        print("   Download Jan AI from: https://jan.ai/")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Start servers
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend")
        sys.exit(1)
    
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend")
        backend_process.terminate()
        sys.exit(1)
    
    # Success!
    print_success_message()
    
    try:
        # Keep script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Servers stopped. Goodbye!")

if __name__ == "__main__":
    main()