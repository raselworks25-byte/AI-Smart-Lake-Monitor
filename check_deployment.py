#!/usr/bin/env python3
"""
Pre-deployment validation script
Checks if your project is ready for production deployment
"""
import os
import sys
from pathlib import Path

def check_file_exists(filename, critical=True):
    """Check if a file exists"""
    exists = Path(filename).exists()
    status = "✓" if exists else "✗"
    level = "CRITICAL" if critical and not exists else "INFO"
    print(f"{status} [{level}] {filename}")
    return exists

def check_env_vars():
    """Check if environment variables are properly configured"""
    print("\n📋 Environment Variables Check:")
    required_vars = ["SECRET_KEY", "INGEST_API_KEY"]
    optional_vars = ["FIREBASE_DATABASE_URL", "FIREBASE_CREDENTIALS_PATH"]
    
    for var in required_vars:
        value = os.getenv(var)
        if value and len(value) > 4:
            print(f"✓ {var}: configured")
        else:
            print(f"✗ {var}: NOT SET or too short (CRITICAL)")
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: configured")
        else:
            print(f"○ {var}: not set (optional)")

def check_config():
    """Check Flask configuration"""
    print("\n⚙️ Configuration Check:")
    
    try:
        from config import Config
        
        if Config.DEBUG:
            print("✗ DEBUG is enabled - DISABLE in production!")
        else:
            print("✓ DEBUG is disabled")
        
        if Config.SECRET_KEY and len(Config.SECRET_KEY) > 20:
            print("✓ SECRET_KEY is set and strong")
        else:
            print("✗ SECRET_KEY is weak or missing")
        
        if Config.INGEST_API_KEY and len(Config.INGEST_API_KEY) > 8:
            print("✓ INGEST_API_KEY is set")
        else:
            print("✗ INGEST_API_KEY is missing or weak")
    except Exception as e:
        print(f"✗ Error checking config: {e}")

def check_requirements():
    """Check if all required packages are in requirements.txt"""
    print("\n📦 Dependencies Check:")
    required = {
        "Flask": "Flask framework",
        "gunicorn": "Production WSGI server",
        "firebase-admin": "Firebase integration",
        "python-dotenv": "Environment variable loading"
    }
    
    with open("requirements.txt", "r") as f:
        content = f.read().lower()
    
    for package, description in required.items():
        if package.lower() in content:
            print(f"✓ {package}: {description}")
        else:
            print(f"✗ {package}: MISSING - {description}")

def check_debug_mode():
    """Check if debug mode is disabled in app.py"""
    print("\n🐛 Debug Mode Check:")
    with open("app.py", "r") as f:
        content = f.read()
    
    if "app.run(debug=True)" in content:
        print("✗ CRITICAL: debug=True found in app.py")
    elif "debug_mode" in content:
        print("✓ Debug mode is conditional")
    else:
        print("✓ Debug mode appears to be handled")

def main():
    print("=" * 60)
    print("🚀 PRE-DEPLOYMENT VALIDATION CHECK")
    print("=" * 60)
    
    print("\n📁 Required Files Check:")
    files_ok = all([
        check_file_exists("config.py"),
        check_file_exists("app.py"),
        check_file_exists("wsgi.py"),
        check_file_exists("requirements.txt"),
        check_file_exists(".env.example"),
        check_file_exists(".gitignore"),
        check_file_exists("Dockerfile", critical=False),
    ])
    
    check_config()
    check_env_vars()
    check_requirements()
    check_debug_mode()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("""
1. Copy .env.example to .env and fill in all values:
   cp .env.example .env

2. Generate a strong SECRET_KEY:
   python -c 'import secrets; print(secrets.token_hex(32))'

3. Test locally with production settings:
   FLASK_ENV=production FLASK_DEBUG=false python app.py

4. Test Docker locally:
   docker-compose up --build

5. Push to your hosting platform:
   - Heroku: git push heroku main
   - Railway: git push origin main
   - DigitalOcean: Follow DEPLOYMENT.md

6. After deployment, test the live endpoints:
   curl https://your-domain.com/login
    """)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
