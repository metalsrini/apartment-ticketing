#!/usr/bin/env python3
"""
Cloud Deployment Script for Apartment Ticketing System
Supports Railway, Render, and Heroku deployment
"""

import os
import sys
import json
import subprocess
import requests
from pathlib import Path

def check_git_repo():
    """Check if current directory is a git repository"""
    try:
        subprocess.run(['git', 'status'], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def initialize_git():
    """Initialize git repository and create initial commit"""
    print("\n🔧 Initializing Git repository...")
    
    # Initialize git
    subprocess.run(['git', 'init'], check=True)
    
    # Create .gitignore
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Database
*.db
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Temporary files
*.tmp
*.temp
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content.strip())
    
    # Add all files
    subprocess.run(['git', 'add', '.'], check=True)
    
    # Initial commit
    subprocess.run(['git', 'commit', '-m', 'Initial commit: Apartment Ticketing System'], check=True)
    
    print("✅ Git repository initialized successfully!")

def create_railway_config():
    """Create Railway configuration files"""
    print("\n🚂 Creating Railway configuration...")
    
    # Create railway.json
    railway_config = {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "python enhanced_app.py",
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 10
        }
    }
    
    with open('railway.json', 'w') as f:
        json.dump(railway_config, f, indent=2)
    
    # Create Procfile for backup
    with open('Procfile', 'w') as f:
        f.write('web: python enhanced_app.py\n')
    
    print("✅ Railway configuration created!")

def create_render_config():
    """Create Render configuration files"""
    print("\n🎨 Creating Render configuration...")
    
    # Create render.yaml
    render_config = {
        "services": [
            {
                "type": "web",
                "name": "apartment-ticketing",
                "env": "python",
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "python enhanced_app.py",
                "envVars": [
                    {
                        "key": "PYTHON_VERSION",
                        "value": "3.11.0"
                    },
                    {
                        "key": "DATABASE_URL",
                        "generateValue": True
                    }
                ]
            }
        ]
    }
    
    with open('render.yaml', 'w') as f:
        json.dump(render_config, f, indent=2)
    
    print("✅ Render configuration created!")

def update_requirements():
    """Update requirements.txt for cloud deployment"""
    print("\n📦 Updating requirements.txt for cloud deployment...")
    
    requirements = [
        "Flask==2.3.3",
        "SQLAlchemy==2.0.21",
        "pandas==2.1.1",
        "openpyxl==3.1.2",
        "python-dotenv==1.0.0",
        "psycopg2-binary==2.9.7",  # For PostgreSQL
        "PyMySQL==1.1.0",          # For MySQL
        "gunicorn==21.2.0"         # WSGI server for production
    ]
    
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(requirements) + '\n')
    
    print("✅ Requirements updated!")

def create_deployment_guide():
    """Create comprehensive deployment guide"""
    print("\n📚 Creating deployment guide...")
    
    guide_content = """
# 🌐 Cloud Deployment Guide

## Quick Start - Railway (Recommended)

### Step 1: Prepare Your Code
```bash
# Run this script first
python deploy_cloud.py
```

### Step 2: Deploy to Railway
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect and deploy your Flask app

### Step 3: Configure Environment Variables
In Railway dashboard, go to Variables tab and add:
```
DATABASE_TYPE=postgresql
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

### Step 4: Add Database
1. In Railway, click "New" → "Database" → "PostgreSQL"
2. Railway will automatically set DATABASE_URL
3. Your app will restart and migrate data automatically

---

## Alternative: Render Deployment

### Step 1: Create Render Account
1. Go to [Render.com](https://render.com)
2. Sign up with GitHub

### Step 2: Create Web Service
1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python enhanced_app.py`
   - **Environment**: `Python 3`

### Step 3: Add Database
1. Create "PostgreSQL" service in Render
2. Copy the database URL
3. Add environment variables in your web service:
   ```
   DATABASE_URL=your-postgresql-url
   DATABASE_TYPE=postgresql
   FLASK_ENV=production
   ```

---

## Alternative: Heroku Deployment

### Step 1: Install Heroku CLI
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Login
heroku login
```

### Step 2: Create Heroku App
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:mini
```

### Step 3: Deploy
```bash
git push heroku main
```

---

## 🔐 Security Configuration

### Environment Variables (Required)
```bash
# Generate a secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

Add these to your cloud platform:
```
SECRET_KEY=your-generated-secret-key
FLASK_ENV=production
DATABASE_TYPE=postgresql
```

### Optional Configuration
```
MAX_CONTENT_LENGTH=16777216  # 16MB file upload limit
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
```

---

## 📱 Access Your Deployed App

Once deployed, your app will be available at:
- **Railway**: `https://your-app-name.up.railway.app`
- **Render**: `https://your-app-name.onrender.com`
- **Heroku**: `https://your-app-name.herokuapp.com`

### Share with Residents
1. Share the URL with all residents
2. They can access from any device with internet
3. No network restrictions - works from anywhere
4. Mobile-friendly interface

---

## 🔧 Troubleshooting

### Common Issues

**App won't start:**
- Check logs in platform dashboard
- Verify all environment variables are set
- Ensure requirements.txt is complete

**Database connection failed:**
- Verify DATABASE_URL is set correctly
- Check if database service is running
- Ensure DATABASE_TYPE matches your database

**502/503 Errors:**
- App might be starting up (wait 1-2 minutes)
- Check if port configuration is correct
- Verify start command is `python enhanced_app.py`

### Getting Help
- Railway: Check deployment logs in dashboard
- Render: View logs in service dashboard
- Heroku: Use `heroku logs --tail`

---

## 💰 Cost Breakdown

### Railway (Recommended)
- **Free Tier**: $5 credit monthly (enough for small apartments)
- **Pro**: $20/month for unlimited usage
- **Database**: Included in free tier

### Render
- **Free Tier**: Limited hours, sleeps after inactivity
- **Starter**: $7/month for always-on service
- **Database**: $7/month for PostgreSQL

### Heroku
- **Free Tier**: Discontinued
- **Basic**: $7/month + $9/month for database

**Recommendation**: Railway offers the best value with generous free tier.
"""
    
    with open('CLOUD_DEPLOYMENT.md', 'w') as f:
        f.write(guide_content.strip())
    
    print("✅ Deployment guide created!")

def update_app_for_cloud():
    """Update enhanced_app.py for cloud deployment"""
    print("\n🔧 Updating app configuration for cloud deployment...")
    
    # Read current app file
    with open('enhanced_app.py', 'r') as f:
        content = f.read()
    
    # Add cloud-specific configurations
    cloud_config = """
# Cloud deployment configuration
if __name__ == '__main__':
    # Get port from environment (for cloud platforms)
    port = int(os.environ.get('PORT', 5002))
    
    # Production vs development settings
    if os.environ.get('FLASK_ENV') == 'production':
        # Production settings
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Development settings
        app.run(host='0.0.0.0', port=port, debug=True)
"""
    
    # Replace the existing if __name__ == '__main__' block
    import re
    pattern = r"if __name__ == '__main__':[\s\S]*$"
    content = re.sub(pattern, cloud_config.strip(), content)
    
    with open('enhanced_app.py', 'w') as f:
        f.write(content)
    
    print("✅ App updated for cloud deployment!")

def main():
    """Main deployment preparation function"""
    print("🚀 Preparing Apartment Ticketing System for Cloud Deployment")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('enhanced_app.py'):
        print("❌ Error: enhanced_app.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    try:
        # Initialize git if not already done
        if not check_git_repo():
            initialize_git()
        else:
            print("✅ Git repository already exists")
        
        # Create configuration files
        create_railway_config()
        create_render_config()
        update_requirements()
        update_app_for_cloud()
        create_deployment_guide()
        
        print("\n" + "=" * 60)
        print("🎉 Cloud deployment preparation complete!")
        print("\n📋 Next Steps:")
        print("1. Push your code to GitHub:")
        print("   git add .")
        print("   git commit -m 'Prepare for cloud deployment'")
        print("   git remote add origin https://github.com/metalsrini/apartment-ticketing.git")
        print("   git push -u origin main")
        print("\n2. Deploy to Railway (Recommended):")
        print("   - Go to https://railway.app")
        print("   - Sign up with GitHub")
        print("   - Deploy from GitHub repo")
        print("   - Add PostgreSQL database")
        print("\n3. Read CLOUD_DEPLOYMENT.md for detailed instructions")
        print("\n🌐 Your app will be accessible worldwide once deployed!")
        
    except Exception as e:
        print(f"❌ Error during preparation: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()