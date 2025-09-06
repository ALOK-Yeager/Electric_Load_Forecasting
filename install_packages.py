#!/usr/bin/env python3
"""
Package Installation Script for Electric Load Forecasting

This script checks for missing packages and installs them.
"""

import sys
import subprocess
import importlib.util
import os
from pathlib import Path

# Packages that need to be installed
REQUIRED_PACKAGES = [
    'numpy',
    'pandas',
    'matplotlib',
    'statsmodels',
    'requests',
    'beautifulsoup4',
    'lxml',
    'schedule',
    'python-telegram-bot',
    'django',
    'tensorflow',
    'python-dotenv',
    'pytz',
    'scikit-learn',
    'asyncio'
]

# Check if a package is installed
def is_package_installed(package_name):
    return importlib.util.find_spec(package_name) is not None

# Install a package using pip
def install_package(package_name):
    print(f"Installing {package_name}...")
    result = subprocess.run([sys.executable, '-m', 'pip', 'install', package_name], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ Successfully installed {package_name}")
        return True
    else:
        print(f"✗ Failed to install {package_name}")
        print(f"  Error: {result.stderr}")
        return False

def main():
    print("Checking and installing required packages for Electric Load Forecasting...")
    
    # Get the project root directory
    project_root = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if requirements.txt exists and use it if available
    req_file = project_root / 'dev-requirements.txt'
    if req_file.exists():
        print(f"Found requirements file: {req_file}")
        print("Installing from requirements file...")
        
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', str(req_file)],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print("✓ Successfully installed all packages from requirements file")
        else:
            print("✗ Failed to install packages from requirements file")
            print(f"  Error: {result.stderr}")
            print("\nFalling back to individual package installation...")
            install_individual_packages()
    else:
        print("No requirements file found. Installing individual packages...")
        install_individual_packages()
    
    print("\nPackage installation complete.")
    print("You may need to restart your development environment for changes to take effect.")

def install_individual_packages():
    missing_packages = []
    
    # Check which packages are missing
    for package in REQUIRED_PACKAGES:
        if not is_package_installed(package.replace('-', '_')):
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Found {len(missing_packages)} missing packages: {', '.join(missing_packages)}")
        
        # Ask user if they want to install missing packages
        install = input("Do you want to install these packages? (y/n): ").lower()
        if install != 'y':
            print("Aborted installation")
            return
        
        # Install missing packages
        success_count = 0
        for package in missing_packages:
            if install_package(package):
                success_count += 1
        
        print(f"\nInstalled {success_count} out of {len(missing_packages)} packages")
    else:
        print("All required packages are already installed")

if __name__ == "__main__":
    main()