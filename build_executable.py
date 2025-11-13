# Build script for creating PDF Tools executable
# Run this script to create a standalone .exe file

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    packages = [
        "PyPDF2==3.0.1",
        "pyinstaller>=6.15.0"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("✅ All packages installed successfully!")

def create_executable():
    """Create the executable file"""
    print("🔨 Creating executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Create single executable file
        "--windowed",                   # No console window (GUI only)
        "--name=PDFTools",              # Name of the executable
        "--distpath=dist",              # Output directory
        "--workpath=build",             # Build directory
        "--specpath=build",             # Spec file location
        "--clean",                      # Clean cache
        "pdf_tool_desktop.py"           # Main Python file
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✅ Executable created successfully!")
        print("📁 You can find 'PDFTools.exe' in the 'dist' folder")
        print("🚀 The executable is ready to run on any Windows PC!")
        
        # Show file info
        exe_path = os.path.join("dist", "PDFTools.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📊 Executable size: {size_mb:.1f} MB")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating executable: {e}")
        return False
    
    return True

def main():
    print("🔄 PDF Tools - Desktop App Builder")
    print("=" * 50)
    
    try:
        # Step 1: Install requirements
        install_requirements()
        print()
        
        # Step 2: Create executable
        if create_executable():
            print()
            print("🎉 SUCCESS!")
            print("Your PDF Tools desktop app is ready!")
            print()
            print("📋 Next steps:")
            print("1. Navigate to the 'dist' folder")
            print("2. Run 'PDFTools.exe'")
            print("3. Enjoy your offline PDF tool!")
            print()
            print("💡 You can copy PDFTools.exe to any Windows PC and it will work without Python installed!")
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
        print("Please make sure you have Python and pip installed properly.")

if __name__ == "__main__":
    main()