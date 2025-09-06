#!/usr/bin/env python3
"""
GitHub Preparation Script for Electric Load Forecasting

This script helps prepare your code for GitHub by:
1. Checking for sensitive information
2. Verifying .gitignore is working
3. Creating an example .env file if it doesn't exist
4. Making other preparations for a clean repository
"""

import os
import re
import shutil
import logging
from pathlib import Path
import subprocess
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Directory containing the project
PROJECT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

def check_env_files():
    """Check for .env files and create an example if needed"""
    env_file = PROJECT_DIR / '.env'
    env_example = PROJECT_DIR / '.env.example'
    
    if env_file.exists():
        logger.info("Found .env file")
        logger.warning("Make sure .env is in your .gitignore before committing!")
        
        # Check if .env contains sensitive information
        with open(env_file, 'r') as f:
            env_content = f.read()
            
        # Look for tokens and keys
        token_pattern = re.compile(r'(TOKEN|KEY|PASSWORD|SECRET).*?=.*?[^\s"\']+')
        matches = token_pattern.findall(env_content)
        if matches:
            logger.warning("Your .env file contains sensitive information:")
            for match in matches:
                logger.warning(f"  - {match}")
            
        # Create .env.example if it doesn't exist
        if not env_example.exists():
            logger.info("Creating .env.example as a template")
            try:
                with open(env_file, 'r') as src, open(env_example, 'w') as dst:
                    for line in src:
                        # Replace actual values with placeholders
                        if '=' in line:
                            key, value = line.split('=', 1)
                            if key.strip() and value.strip() and not line.strip().startswith('#'):
                                dst.write(f"{key}=YOUR_{key.strip()}_HERE\n")
                            else:
                                dst.write(line)
                        else:
                            dst.write(line)
                logger.info("Created .env.example with placeholders")
            except Exception as e:
                logger.error(f"Failed to create .env.example: {e}")
    else:
        logger.warning("No .env file found. You should create one from .env.example")
        if env_example.exists():
            logger.info("Found .env.example - use this as a template")

def check_gitignore():
    """Check if .gitignore file exists and contains necessary entries"""
    gitignore_path = PROJECT_DIR / '.gitignore'
    necessary_entries = ['.env', '*.pem', '*.key', '__pycache__/', '*.pyc', 'db.sqlite3']
    
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            content = f.read()
            
        missing_entries = []
        for entry in necessary_entries:
            if entry not in content:
                missing_entries.append(entry)
                
        if missing_entries:
            logger.warning("Your .gitignore is missing these important entries:")
            for entry in missing_entries:
                logger.warning(f"  - {entry}")
            
            # Add the missing entries
            add_to_gitignore = input("Would you like to add these entries to .gitignore? (y/n): ").lower()
            if add_to_gitignore == 'y':
                with open(gitignore_path, 'a') as f:
                    f.write("\n# Added by prepare_for_github.py\n")
                    for entry in missing_entries:
                        f.write(f"{entry}\n")
                logger.info("Added missing entries to .gitignore")
    else:
        logger.error("No .gitignore file found! This is crucial for security.")
        create_gitignore = input("Would you like to create a basic .gitignore? (y/n): ").lower()
        if create_gitignore == 'y':
            with open(gitignore_path, 'w') as f:
                f.write("# Python\n")
                f.write("__pycache__/\n")
                f.write("*.py[cod]\n")
                f.write("*$py.class\n")
                f.write("*.so\n")
                f.write("*.egg-info/\n")
                f.write("\n# Django\n")
                f.write("*.log\n")
                f.write("db.sqlite3\n")
                f.write("media/\n")
                f.write("\n# Environment\n")
                f.write(".env\n")
                f.write("env/\n")
                f.write("venv/\n")
                f.write("\n# Credentials\n")
                f.write("*.pem\n")
                f.write("*.key\n")
            logger.info("Created a basic .gitignore file")

def check_for_pem_files():
    """Check for .pem files that should not be committed"""
    pem_files = list(PROJECT_DIR.glob('**/*.pem'))
    key_files = list(PROJECT_DIR.glob('**/*.key'))
    
    if pem_files:
        logger.warning("Found .pem files that should not be committed:")
        for pem in pem_files:
            logger.warning(f"  - {pem.relative_to(PROJECT_DIR)}")
            
    if key_files:
        logger.warning("Found .key files that should not be committed:")
        for key in key_files:
            logger.warning(f"  - {key.relative_to(PROJECT_DIR)}")

def check_github_settings():
    """Check GitHub configuration and settings"""
    try:
        # Check if git is initialized
        if not (PROJECT_DIR / '.git').exists():
            logger.warning("Git is not initialized in this directory")
            init_git = input("Would you like to initialize git? (y/n): ").lower()
            if init_git == 'y':
                subprocess.run(['git', 'init'], cwd=PROJECT_DIR)
                logger.info("Initialized git repository")
        else:
            logger.info("Git repository is already initialized")
            
        # Check remote
        try:
            result = subprocess.run(
                ['git', 'remote', '-v'], 
                cwd=PROJECT_DIR, 
                capture_output=True, 
                text=True
            )
            if result.stdout:
                logger.info(f"Git remotes configured: \n{result.stdout}")
            else:
                logger.warning("No git remote configured")
                add_remote = input("Would you like to add a remote? (y/n): ").lower()
                if add_remote == 'y':
                    remote_url = input("Enter your GitHub repository URL: ")
                    subprocess.run(['git', 'remote', 'add', 'origin', remote_url], cwd=PROJECT_DIR)
                    logger.info(f"Added remote 'origin' with URL {remote_url}")
        except Exception as e:
            logger.error(f"Error checking git remotes: {e}")
    
    except Exception as e:
        logger.error(f"Error checking GitHub settings: {e}")

def cleanup_pyc_files():
    """Remove compiled Python files"""
    try:
        pycache_dirs = list(PROJECT_DIR.glob('**/__pycache__'))
        pyc_files = list(PROJECT_DIR.glob('**/*.pyc'))
        
        for pycache in pycache_dirs:
            shutil.rmtree(pycache)
            logger.info(f"Removed {pycache.relative_to(PROJECT_DIR)}")
            
        for pyc in pyc_files:
            pyc.unlink()
            logger.info(f"Removed {pyc.relative_to(PROJECT_DIR)}")
            
        logger.info("Cleanup of compiled Python files complete")
    except Exception as e:
        logger.error(f"Error cleaning up compiled files: {e}")

def main():
    """Main function to run all checks"""
    logger.info("Preparing your Electric Load Forecasting project for GitHub...")
    
    check_env_files()
    print()
    
    check_gitignore()
    print()
    
    check_for_pem_files()
    print()
    
    cleanup_pyc_files()
    print()
    
    check_github_settings()
    print()
    
    logger.info("Preparation complete! Review the warnings above before pushing to GitHub.")
    logger.info("Make sure to follow these security best practices:")
    logger.info("1. Never commit .env files with real credentials")
    logger.info("2. Keep your .gitignore updated")
    logger.info("3. Use environment variables for sensitive information")
    logger.info("4. Remove any API keys or tokens from code comments")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nPreparation interrupted. Make sure to complete security checks manually.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during preparation: {e}")
        sys.exit(1)