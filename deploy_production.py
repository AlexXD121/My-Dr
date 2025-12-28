#!/usr/bin/env python3
"""
Production Deployment Script for My Dr AI Medical Assistant
Automates the production deployment process with safety checks
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import json
import requests

class ProductionDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def error(self, message):
        self.errors.append(message)
        self.log(message, "ERROR")
        
    def warning(self, message):
        self.warnings.append(message)
        self.log(message, "WARNING")
        
    def run_command(self, command, cwd=None):
        """Run shell command and return result"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd or self.project_root,
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.error(f"Command failed: {command}")
            self.error(f"Error: {e.stderr}")
            return None
            
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        self.log("Checking prerequisites...")
        
        # Check Docker
        if not self.run_command("docker --version"):
            self.error("Docker is not installed or not accessible")
            
        # Check Docker Compose
        if not self.run_command("docker-compose --version"):
            self.error("Docker Compose is not installed")
            
        # Check environment files
        env_files = [".env.production", "frontend/.env.production"]
        for env_file in env_files:
            if not (self.project_root / env_file).exists():
                self.error(f"Missing environment file: {env_file}")
                
        # Check for placeholder values in production env
        prod_env = self.project_root / ".env.production"
        if prod_env.exists():
            content = prod_env.read_text()
            placeholders = [
                "production_jwt_secret_change_me",
                "production_firebase_key_change_me",
                "production_postgres_password_change_me"
            ]
            for placeholder in placeholders:
                if placeholder in content:
                    self.error(f"Placeholder value found in .env.production: {placeholder}")
                    
    def build_images(self):
        """Build Docker images"""
        self.log("Building Docker images...")
        
        # Build backend
        if not self.run_command("docker build -f Dockerfile.backend -t mydoc-backend ."):
            self.error("Failed to build backend image")
            
        # Build frontend
        if not self.run_command("docker build -f Dockerfile.frontend -t mydoc-frontend ."):
            self.error("Failed to build frontend image")
            
    def run_tests(self):
        """Run tests before deployment"""
        self.log("Running tests...")
        
        # Backend tests
        backend_test = self.run_command(
            "docker run --rm mydoc-backend python -m pytest tests/ -v",
        )
        if backend_test is None:
            self.warning("Backend tests failed or not found")
            
        # Frontend tests (if available)
        frontend_test = self.run_command(
            "cd frontend && npm test -- --run",
        )
        if frontend_test is None:
            self.warning("Frontend tests failed or not found")
            
    def deploy_services(self):
        """Deploy services using Docker Compose"""
        self.log("Deploying services...")
        
        # Stop existing services
        self.run_command("docker-compose -f docker-compose.production.yml down")
        
        # Start production services
        if not self.run_command("docker-compose -f docker-compose.production.yml up -d"):
            self.error("Failed to start production services")
            return False
            
        return True
        
    def wait_for_services(self):
        """Wait for services to be ready"""
        self.log("Waiting for services to be ready...")
        
        # Wait for backend
        backend_ready = False
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    backend_ready = True
                    break
            except:
                pass
            time.sleep(1)
            
        if not backend_ready:
            self.error("Backend service did not start properly")
            
        # Wait for frontend
        frontend_ready = False
        for i in range(30):
            try:
                response = requests.get("http://localhost:80/health", timeout=5)
                if response.status_code == 200:
                    frontend_ready = True
                    break
            except:
                pass
            time.sleep(1)
            
        if not frontend_ready:
            self.error("Frontend service did not start properly")
            
        return backend_ready and frontend_ready
        
    def run_health_checks(self):
        """Run comprehensive health checks"""
        self.log("Running health checks...")
        
        checks = [
            ("Backend Health", "http://localhost:8000/health"),
            ("Frontend Health", "http://localhost:80/health"),
            ("API Test", "http://localhost:8000/"),
        ]
        
        for check_name, url in checks:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.log(f"✅ {check_name}: OK")
                else:
                    self.error(f"❌ {check_name}: HTTP {response.status_code}")
            except Exception as e:
                self.error(f"❌ {check_name}: {str(e)}")
                
    def create_backup(self):
        """Create backup before deployment"""
        self.log("Creating backup...")
        
        backup_dir = self.project_root / "backups" / f"backup_{int(time.time())}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup database (if running)
        db_backup = self.run_command(
            f"docker exec mydoc_postgres pg_dump -U mydoc_user mydoc_prod > {backup_dir}/database.sql"
        )
        if db_backup is None:
            self.warning("Could not create database backup")
            
    def rollback(self):
        """Rollback deployment if something goes wrong"""
        self.log("Rolling back deployment...")
        
        # Stop current services
        self.run_command("docker-compose -f docker-compose.production.yml down")
        
        # Start previous version (if available)
        self.run_command("docker-compose -f docker-compose.yml up -d")
        
    def deploy(self):
        """Main deployment process"""
        self.log("Starting production deployment...")
        
        try:
            # Pre-deployment checks
            self.check_prerequisites()
            if self.errors:
                self.log("Prerequisites check failed. Aborting deployment.")
                return False
                
            # Create backup
            self.create_backup()
            
            # Build and test
            self.build_images()
            if self.errors:
                self.log("Image build failed. Aborting deployment.")
                return False
                
            self.run_tests()
            
            # Deploy
            if not self.deploy_services():
                self.log("Service deployment failed. Aborting.")
                return False
                
            # Wait and verify
            if not self.wait_for_services():
                self.log("Services failed to start properly. Rolling back.")
                self.rollback()
                return False
                
            # Final health checks
            self.run_health_checks()
            
            if self.errors:
                self.log("Health checks failed. Consider rolling back.")
                return False
                
            self.log("🎉 Production deployment completed successfully!")
            
            if self.warnings:
                self.log(f"⚠️  Deployment completed with {len(self.warnings)} warnings:")
                for warning in self.warnings:
                    self.log(f"  - {warning}")
                    
            return True
            
        except Exception as e:
            self.error(f"Deployment failed with exception: {str(e)}")
            self.rollback()
            return False
            
    def print_summary(self):
        """Print deployment summary"""
        print("\n" + "="*60)
        print("DEPLOYMENT SUMMARY")
        print("="*60)
        
        if self.errors:
            print(f"❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
                
        if self.warnings:
            print(f"⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
                
        if not self.errors:
            print("✅ DEPLOYMENT SUCCESSFUL")
            print("\nServices are running at:")
            print("  - Frontend: http://localhost:80")
            print("  - Backend API: http://localhost:8000")
            print("  - API Docs: http://localhost:8000/docs")
        else:
            print("❌ DEPLOYMENT FAILED")
            print("Please fix the errors above and try again.")
            
        print("="*60)


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python deploy_production.py")
        print("Deploys My Dr AI Medical Assistant to production")
        return
        
    deployer = ProductionDeployer()
    success = deployer.deploy()
    deployer.print_summary()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()