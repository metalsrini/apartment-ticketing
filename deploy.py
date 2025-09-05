#!/usr/bin/env python3
"""
Deployment script for Apartment Issue Ticketing System
This script helps with easy setup and deployment of the application.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("   Required: Python 3.8 or higher")
        return False

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_port_availability(port=5001):
    """Check if the specified port is available"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            print(f"✅ Port {port} is available")
            return True
    except OSError:
        print(f"⚠️  Port {port} is in use")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['templates', 'static']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created/verified")

def setup_environment():
    """Set up the environment"""
    print("🔧 Setting up environment...")
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ app.py not found. Please run this script from the project directory.")
        return False
    
    # Create directories
    create_directories()
    
    # Check port
    check_port_availability()
    
    return True

def start_application():
    """Start the Flask application"""
    print("🚀 Starting the application...")
    try:
        # Start the application
        subprocess.Popen([sys.executable, "app.py"])
        print("✅ Application started successfully!")
        print("\n🌐 Access your application at: http://localhost:5001")
        print("\n📋 Available features:")
        print("   • Submit maintenance tickets")
        print("   • View and filter tickets")
        print("   • Export data to Excel")
        print("   • Real-time statistics")
        print("\n⏹️  To stop the server, press Ctrl+C in the terminal")
        return True
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False

def show_system_info():
    """Display system information"""
    print("=" * 60)
    print("🏢 APARTMENT ISSUE TICKETING SYSTEM")
    print("=" * 60)
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"Current Directory: {os.getcwd()}")
    print("=" * 60)

def main():
    """Main deployment function"""
    show_system_info()
    
    print("\n🔍 Running pre-deployment checks...\n")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Setup environment
    if not setup_environment():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    print("\n✅ All checks passed! Ready to deploy.\n")
    
    # Ask user if they want to start the application
    response = input("🚀 Start the application now? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        start_application()
    else:
        print("\n📝 To start the application later, run: python app.py")
        print("🌐 Then access it at: http://localhost:5001")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Deployment cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)