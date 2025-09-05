#!/usr/bin/env python3
"""
Local Network Deployment Script for Apartment Ticketing System
This script sets up the system for local network access by all residents.
"""

import os
import sys
import socket
import subprocess
import platform
from pathlib import Path

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def check_port_availability(port=5002):
    """Check if the specified port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False

def setup_environment():
    """Set up environment variables for local deployment"""
    os.environ['USE_DATABASE'] = 'true'
    os.environ['FLASK_ENV'] = 'production'
    print("✅ Environment configured for local network deployment")

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import pandas
        import sqlalchemy
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install -r requirements.txt")
        return False

def create_deployment_info(local_ip, port=5002):
    """Create deployment information file for residents"""
    info_content = f"""# Apartment Ticketing System - Access Information

## How to Access the System

### From Your Device (Phone/Computer/Tablet)

1. **Connect to the same WiFi network** as the server
2. **Open your web browser** (Chrome, Safari, Firefox, etc.)
3. **Go to:** http://{local_ip}:{port}

### Quick Access Links
- **Main System:** http://{local_ip}:{port}
- **Create Ticket:** http://{local_ip}:{port}/#create-ticket
- **View Tickets:** http://{local_ip}:{port}/tickets (requires login)
- **Reports:** http://{local_ip}:{port}/reports (admin only)

### Login Credentials
- **Admin Access:** 
  - Username: admin
  - Password: admin
- **Super Admin Access:**
  - Username: superadmin  
  - Password: superadmin

### System Features
✅ Create maintenance tickets
✅ Track ticket status
✅ Assign tickets to staff
✅ Generate reports
✅ Export data to Excel
✅ Multi-user access
✅ Real-time updates

### Troubleshooting
- **Can't access?** Make sure you're on the same WiFi network
- **Page won't load?** Check the IP address: {local_ip}
- **Need help?** Contact the system administrator

### Server Information
- **Server IP:** {local_ip}
- **Port:** {port}
- **Database:** SQLite (local file)
- **Concurrent Users:** Up to 50 simultaneous users

---
*Generated on {platform.node()} at {socket.gethostname()}*
"""
    
    with open('RESIDENT_ACCESS_INFO.md', 'w') as f:
        f.write(info_content)
    
    print(f"📋 Created RESIDENT_ACCESS_INFO.md with access instructions")

def print_network_info(local_ip, port=5002):
    """Print network access information"""
    print("\n" + "="*60)
    print("🏠 APARTMENT TICKETING SYSTEM - LOCAL NETWORK DEPLOYMENT")
    print("="*60)
    print(f"\n🌐 Server running on: http://{local_ip}:{port}")
    print(f"📱 Residents can access from any device on the same WiFi")
    print(f"\n📋 Access Instructions:")
    print(f"   1. Connect to the same WiFi network")
    print(f"   2. Open web browser")
    print(f"   3. Go to: http://{local_ip}:{port}")
    print(f"\n🔐 Admin Login:")
    print(f"   Username: admin")
    print(f"   Password: admin")
    print(f"\n👥 Concurrent Users: Up to 50 residents simultaneously")
    print(f"💾 Database: Local SQLite (all data saved)")
    print(f"\n📄 Detailed instructions saved to: RESIDENT_ACCESS_INFO.md")
    print("\n⏹️  To stop the server: Press Ctrl+C")
    print("="*60)

def main():
    """Main deployment function"""
    print("🚀 Setting up Local Network Deployment...\n")
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Get local IP
    local_ip = get_local_ip()
    port = 5002
    
    # Check port availability
    if not check_port_availability(port):
        print(f"❌ Port {port} is already in use")
        print("   Please stop any running servers and try again")
        return False
    
    # Setup environment
    setup_environment()
    
    # Create deployment info
    create_deployment_info(local_ip, port)
    
    # Print network information
    print_network_info(local_ip, port)
    
    # Start the server
    print("\n🔄 Starting server...\n")
    
    try:
        # Import and run the Flask app
        sys.path.append(os.getcwd())
        from enhanced_app import app, initialize_csv, initialize_database
        
        # Initialize systems
        initialize_csv()
        initialize_database()
        
        # Run the server
        app.run(
            debug=False,  # Disable debug for production
            host='0.0.0.0',  # Listen on all interfaces
            port=port,
            threaded=True  # Handle multiple requests
        )
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Server stopped by user")
        print("✅ Deployment completed successfully")
        return True
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print("\n🎉 Local network deployment completed!")
    else:
        print("\n❌ Deployment failed. Please check the errors above.")
        sys.exit(1)