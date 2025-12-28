# 📦 MyDoc AI - Installation Guide

This guide will help you set up MyDoc AI on your local machine or server.

## 📋 System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Internet**: Stable internet connection for AI features

### Software Requirements
- **Node.js**: Version 18.0 or higher
- **npm**: Version 8.0 or higher (comes with Node.js)
- **Python**: Version 3.8 or higher
- **pip**: Python package installer
- **Git**: Version control system

## 🔧 Installation Steps

### Step 1: Install Prerequisites

#### Windows
1. **Install Node.js**
   - Download from [nodejs.org](https://nodejs.org/)
   - Choose the LTS version
   - Run the installer and follow the setup wizard

2. **Install Python**
   - Download from [python.org](https://python.org/)
   - Choose Python 3.8+ version
   - ✅ Check "Add Python to PATH" during installation

3. **Install Git**
   - Download from [git-scm.com](https://git-scm.com/)
   - Run the installer with default settings

#### macOS
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js
brew install node

# Install Python
brew install python

# Install Git
brew install git
```

#### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt update

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python
sudo apt install python3 python3-pip

# Install Git
sudo apt install git
```

### Step 2: Clone the Repository

```bash
# Clone the repository
git clone <your-repository-url>
cd MyDoc-AI

# Verify the project structure
ls -la
```

### Step 3: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env file with your configuration (optional)
# nano .env  # Linux/macOS
# notepad .env  # Windows
```

### Step 4: Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install Node.js dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env file if needed (optional)
```

### Step 5: Database Setup

The application uses SQLite by default (no additional setup required). For PostgreSQL:

```bash
# Install PostgreSQL (optional)
# Windows: Download from postgresql.org
# macOS: brew install postgresql
# Linux: sudo apt install postgresql postgresql-contrib

# Create database (if using PostgreSQL)
createdb mydoc_ai

# Update .env file with database URL
# DATABASE_URL=postgresql://username:password@localhost/mydoc_ai
```

## 🚀 Running the Application

### Development Mode

1. **Start the Backend**
   ```bash
   cd backend
   # Activate virtual environment if not already active
   source venv/bin/activate  # macOS/Linux
   # venv\Scripts\activate   # Windows
   
   # Start the server
   python main.py
   ```
   Backend will be available at: http://localhost:8000

2. **Start the Frontend** (in a new terminal)
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend will be available at: http://localhost:5173

### Production Mode

1. **Build Frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Start Backend in Production**
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## 🔧 Configuration

### Backend Configuration (.env)
```env
# Database
DATABASE_URL=sqlite:///./mydoc.db

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS Settings
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Frontend Configuration (.env)
```env
# API Base URL
VITE_API_BASE_URL=http://localhost:8000

# App Settings
VITE_APP_NAME=MyDoc AI
VITE_APP_VERSION=1.0.0
```

## 🧪 Verification

### Test Backend
```bash
# Test API endpoint
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "timestamp": "..."}
```

### Test Frontend
1. Open http://localhost:5173 in your browser
2. You should see the MyDoc AI interface
3. Try sending a test message in the chat

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

#### Python Module Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt
```

#### Node.js Dependencies Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json  # macOS/Linux
rmdir /s node_modules & del package-lock.json  # Windows
npm install
```

#### Database Connection Issues
```bash
# Check SQLite database file
ls -la backend/mydoc.db

# Reset database (if needed)
rm backend/mydoc.db
python backend/main.py  # Will recreate database
```

### Performance Issues

#### Slow Frontend Loading
```bash
# Build for production
npm run build

# Serve built files
npm run preview
```

#### High Memory Usage
- Close unnecessary applications
- Increase virtual memory/swap space
- Use production builds instead of development

## 🔒 Security Considerations

### Development Environment
- Keep `.env` files secure and never commit them
- Use strong passwords for database connections
- Enable firewall for production deployments

### Production Deployment
- Use HTTPS certificates
- Configure proper CORS origins
- Set up rate limiting
- Use environment variables for sensitive data
- Regular security updates

## 📊 System Monitoring

### Check System Resources
```bash
# Check disk space
df -h

# Check memory usage
free -h  # Linux
top      # macOS/Linux
```

### Application Logs
```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend build logs
npm run build --verbose
```

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs** for error messages
2. **Verify prerequisites** are correctly installed
3. **Check port availability** (8000, 5173)
4. **Review configuration files** (.env)
5. **Restart services** and try again

### Support Channels
- 📧 Email: support@mydocai.com
- 🐛 Issues: Create a GitHub issue
- 📖 Documentation: Check USER_MANUAL.md

---

**Installation complete! 🎉 You're ready to use MyDoc AI!**