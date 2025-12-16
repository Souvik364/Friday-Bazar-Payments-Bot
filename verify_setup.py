"""
Setup Verification Script
Run this before starting the bot to verify configuration.
"""

import sys
import os

def check_python_version():
    """Check if Python version is 3.10 or higher."""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.10+")
        return False

def check_dependencies():
    """Check if all required packages are installed."""
    print("\n🔍 Checking dependencies...")
    required = ['aiogram', 'dotenv', 'qrcode', 'PIL']
    missing = []
    
    for package in required:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            elif package == 'PIL':
                __import__('PIL')
            else:
                __import__(package)
            print(f"✅ {package} - Installed")
        except ImportError:
            print(f"❌ {package} - NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Install missing packages: pip install -r requirements.txt")
        return False
    return True

def check_env_file():
    """Check if .env file exists and contains required variables."""
    print("\n🔍 Checking .env configuration...")
    
    if not os.path.exists('.env'):
        print("❌ .env file NOT found")
        print("   Create .env file with:")
        print("   BOT_TOKEN=your_token")
        print("   ADMIN_ID=your_id")
        return False
    
    print("✅ .env file found")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    bot_token = os.getenv('BOT_TOKEN')
    admin_id = os.getenv('ADMIN_ID')
    
    if not bot_token or bot_token == 'your_bot_token_here':
        print("❌ BOT_TOKEN not configured properly")
        return False
    print("✅ BOT_TOKEN configured")
    
    if not admin_id or admin_id == 'your_admin_id_here':
        print("❌ ADMIN_ID not configured properly")
        return False
    
    try:
        int(admin_id)
        print("✅ ADMIN_ID configured")
    except ValueError:
        print("❌ ADMIN_ID must be a number")
        return False
    
    return True

def check_file_structure():
    """Check if all required files exist."""
    print("\n🔍 Checking file structure...")
    required_files = [
        'bot.py',
        'config.py',
        'requirements.txt',
        'handlers/__init__.py',
        'handlers/start.py',
        'handlers/premium.py',
        'handlers/admin.py',
        'utils/__init__.py',
        'utils/qr_generator.py',
        'utils/timer.py'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    print("=" * 50)
    print("🤖 Telegram Premium Bot - Setup Verification")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_file_structure(),
        check_env_file()
    ]
    
    print("\n" + "=" * 50)
    if all(checks):
        print("✅ All checks passed! You're ready to run the bot.")
        print("\nRun the bot with: python bot.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
    print("=" * 50)

if __name__ == "__main__":
    main()
