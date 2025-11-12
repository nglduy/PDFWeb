#!/usr/bin/env python3

"""
Test script to validate the Python PDF application setup
"""

import os
import sys

def check_python_version():
    """Check if Python version is adequate"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Requires 3.8+)")
        return False

def check_files():
    """Check if required files exist"""
    required_files = [
        'app.py',
        'requirements.txt',
        'templates/index.html',
        'static/styles.css',
        'static/script.js'
    ]
    
    print('📁 Checking required files...')
    all_present = True
    
    for file in required_files:
        exists = os.path.exists(file)
        print(f"   {'✅' if exists else '❌'} {file}")
        if not exists:
            all_present = False
    
    # Check uploads directory
    uploads_exists = os.path.exists('uploads')
    print(f"   {'✅' if uploads_exists else '❌'} uploads/ directory")
    
    return all_present and uploads_exists

def check_dependencies():
    """Check if Python packages can be imported"""
    print('\n📦 Checking Python dependencies...')
    dependencies = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'PyPDF2': 'PyPDF2',
        'werkzeug': 'Werkzeug'
    }
    
    all_imported = True
    
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name}")
            all_imported = False
    
    return all_imported

def main():
    print('🔍 PDF Tools - Python Setup Validation\n')
    
    # Check Python version
    print('🐍 Checking Python version...')
    python_ok = check_python_version()
    
    # Check files
    files_ok = check_files()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    print('\n🚀 Setup Status:')
    
    if not python_ok:
        print('   ❌ Please install Python 3.8 or higher')
        print('      Download from: https://python.org')
    
    if not files_ok:
        print('   ❌ Some required files are missing!')
    
    if not deps_ok:
        print('   ❌ Missing dependencies. Run: pip install -r requirements.txt')
    
    if python_ok and files_ok and deps_ok:
        print('   ✅ Everything looks good!')
        print('\n🎯 Next steps:')
        print('   1. Run: python app.py')
        print('   2. Open: http://localhost:5000')
    else:
        print('\n🔧 Required actions:')
        if not python_ok:
            print('   • Install/upgrade Python')
        if not deps_ok:
            print('   • Install dependencies: pip install -r requirements.txt')
        if not files_ok:
            print('   • Ensure all project files are present')
    
    print('\n📖 For deployment help, see DEPLOYMENT.md')
    print('🐛 For issues, check the README.md\n')

if __name__ == '__main__':
    main()