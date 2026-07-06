#!/usr/bin/env python3
"""
Configuration Generator - Generates all required deployment values
"""
import secrets
import sys
from pathlib import Path

def generate_secret_key():
    """Generate SECRET_KEY for Flask session encryption"""
    return secrets.token_hex(32)

def generate_api_key():
    """Generate INGEST_API_KEY for Raspberry Pi authentication"""
    return secrets.token_urlsafe(32)

def generate_env_file():
    """Generate .env file with all values"""
    secret_key = generate_secret_key()
    api_key = generate_api_key()
    
    env_content = f"""# Generated Configuration - {Path(__file__).parent.name}
# DO NOT COMMIT THIS FILE TO GIT

# === REQUIRED FOR PRODUCTION ===
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY={secret_key}
INGEST_API_KEY={api_key}
APP_NAME=Smart AI Lake Monitoring

# === OPTIONAL: Firebase Configuration ===
# If you don't have Firebase, leave these blank
FIREBASE_DATABASE_URL=
FIREBASE_STORAGE_BUCKET=
FIREBASE_CREDENTIALS_PATH=

# === SERVER CONFIG ===
PORT=5000
"""
    return env_content, secret_key, api_key

def main():
    print("=" * 70)
    print("🔑 CONFIGURATION GENERATOR")
    print("=" * 70)
    
    try:
        env_content, secret_key, api_key = generate_env_file()
        
        print("\n✅ Generated Configuration Values:\n")
        print(f"SECRET_KEY = {secret_key}")
        print(f"INGEST_API_KEY = {api_key}")
        
        print("\n" + "=" * 70)
        print("📋 Environment Variables to Set on Your Hosting Platform:")
        print("=" * 70)
        print(f"""
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY={secret_key}
INGEST_API_KEY={api_key}
APP_NAME=Smart AI Lake Monitoring
PORT=5000
        """)
        
        print("\n" + "=" * 70)
        print("💾 Saving to .env file...")
        print("=" * 70)
        
        env_path = Path(".env")
        if env_path.exists():
            print(f"⚠️  .env already exists. Skipping (rename existing to backup)")
            response = input("Overwrite? (y/n): ").strip().lower()
            if response != 'y':
                print("Cancelled.")
                return
        
        env_path.write_text(env_content)
        print(f"✅ Created: {env_path.absolute()}")
        print("\n⚠️  WARNING: This file contains secrets!")
        print("✅ Already in .gitignore (safe to commit git files)")
        
        print("\n" + "=" * 70)
        print("🚀 NEXT STEPS:")
        print("=" * 70)
        print("""
1. Copy the SECRET_KEY and INGEST_API_KEY values above

2. Go to your hosting platform (Railway, Heroku, DigitalOcean, etc.)

3. Add these environment variables to your platform:
   - FLASK_ENV = production
   - FLASK_DEBUG = false
   - SECRET_KEY = <paste value from above>
   - INGEST_API_KEY = <paste value from above>

4. Deploy your application

5. Test with:
   curl https://your-domain.com/login

For Firebase (optional):
- See CONFIGURATION_GUIDE.md section 3 & 4
- Get FIREBASE_DATABASE_URL from Firebase Console
- Upload service account JSON and set FIREBASE_CREDENTIALS_PATH

📚 Full guide: CONFIGURATION_GUIDE.md
🚀 Deployment guide: DEPLOYMENT.md
        """)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
