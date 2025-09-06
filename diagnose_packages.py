#!/usr/bin/env python3
"""
Package Diagnosis Tool for Electric Load Forecasting

This script helps identify package compatibility issues and version mismatches.
"""

import importlib
import sys
import os
import pkg_resources
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def check_package(package_name, min_version=None):
    """Check if a package is installed and its version"""
    try:
        pkg = importlib.import_module(package_name)
        version = getattr(pkg, '__version__', None)
        if not version:
            try:
                version = pkg_resources.get_distribution(package_name).version
            except:
                version = "Unknown"
                
        if min_version and version != "Unknown":
            parts = [int(x) for x in version.split('.')]
            min_parts = [int(x) for x in min_version.split('.')]
            meets_min = parts >= min_parts
            status = "✅" if meets_min else "❌"
            logger.info(f"{status} {package_name}: Version {version} (minimum required: {min_version})")
            return meets_min
        else:
            logger.info(f"✅ {package_name}: Version {version}")
            return True
            
    except ImportError:
        logger.info(f"❌ {package_name}: Not installed")
        return False

def check_statsmodels_compatibility():
    """Perform specific checks for statsmodels compatibility"""
    try:
        import statsmodels
        version = statsmodels.__version__
        logger.info(f"Statsmodels version: {version}")
        
        # Check if ARIMAResults.load exists
        try:
            from statsmodels.tsa.arima_model import ARIMAResults
            if hasattr(ARIMAResults, 'load'):
                logger.info("✅ ARIMAResults.load exists")
            else:
                logger.info("❌ ARIMAResults.load does not exist")
                logger.info("   Suggested fix: Use pickle.load instead or upgrade/downgrade statsmodels")
        except ImportError:
            logger.info("❌ Cannot import ARIMAResults from statsmodels.tsa.arima_model")
        
        # Check if SARIMAX.load exists
        try:
            from statsmodels.tsa.api import SARIMAX
            if hasattr(SARIMAX, 'load'):
                logger.info("✅ SARIMAX.load exists")
            else:
                logger.info("❌ SARIMAX.load does not exist")
                logger.info("   Suggested fix: Create a compatibility layer")
        except ImportError:
            logger.info("❌ Cannot import SARIMAX from statsmodels.tsa.api")
        
    except ImportError:
        logger.info("❌ statsmodels is not installed")

def check_bs4_compatibility():
    """Check BeautifulSoup compatibility issues"""
    try:
        from bs4 import BeautifulSoup
        
        # Create a simple HTML and check methods
        html = "<html><body><table><tr><td>Cell</td></tr></table></body></html>"
        soup = BeautifulSoup(html, "lxml")
        
        table = soup.find("table")
        
        if hasattr(table, 'find_all'):
            logger.info("✅ BeautifulSoup find_all method exists")
        else:
            logger.info("❌ BeautifulSoup find_all method does not exist")
            
        if hasattr(table, 'findAll'):
            logger.info("✅ BeautifulSoup findAll method exists")
        else:
            logger.info("❌ BeautifulSoup findAll method does not exist")
            
        tr = table.find("tr")
        if hasattr(tr, 'find_all'):
            logger.info("✅ BeautifulSoup tr.find_all method exists")
        else:
            logger.info("❌ BeautifulSoup tr.find_all method does not exist")
            
        if hasattr(tr, 'findChildren'):
            logger.info("✅ BeautifulSoup tr.findChildren method exists")
        else:
            logger.info("❌ BeautifulSoup tr.findChildren method does not exist")
            
    except ImportError as e:
        logger.info(f"❌ BeautifulSoup issue: {e}")
        
    except Exception as e:
        logger.info(f"❌ BeautifulSoup error: {e}")

def check_pandas_compatibility():
    """Check pandas compatibility issues"""
    try:
        import pandas as pd
        
        # Test read_csv with various parameter formats
        try:
            # Create a test CSV
            with open('test.csv', 'w') as f:
                f.write('datetime,value\n')
                f.write('2023-01-01 00:00,100\n')
                f.write('2023-01-01 00:30,110\n')
            
            # Test with single string index_col
            df1 = pd.read_csv('test.csv', index_col='datetime')
            logger.info("✅ pd.read_csv with string index_col works")
            
            # Test with list index_col
            df2 = pd.read_csv('test.csv', index_col=['datetime'])
            logger.info("✅ pd.read_csv with list index_col works")
            
            # Test with parse_dates
            df3 = pd.read_csv('test.csv', index_col='datetime', parse_dates=True)
            logger.info("✅ pd.read_csv with parse_dates=True works")
            
            df4 = pd.read_csv('test.csv', index_col='datetime', parse_dates=['datetime'])
            logger.info("✅ pd.read_csv with parse_dates=list works")
            
            os.remove('test.csv')
        
        except Exception as e:
            logger.info(f"❌ pandas.read_csv issue: {e}")
    
    except ImportError:
        logger.info("❌ pandas is not installed")

def main():
    """Main function"""
    logger.info("Checking required packages...")
    
    # Check core packages
    packages = [
        ("numpy", "1.19.0"),
        ("pandas", "1.0.0"),
        ("matplotlib", "3.3.0"),
        ("statsmodels", "0.12.0"),
        ("scikit-learn", "0.23.0"),
        ("requests", "2.23.0"),
        ("beautifulsoup4", "4.9.0"),
        ("lxml", "4.5.0"),
        ("schedule", "1.0.0"),
        ("telegram", "0.0.1"),  # python-telegram-bot
        ("tensorflow", "2.0.0"),
        ("django", "3.0.0"),
        ("python-dotenv", "0.13.0"),
    ]
    
    for package, min_version in packages:
        check_package(package, min_version)
    
    logger.info("\nPerforming specific compatibility checks...")
    check_statsmodels_compatibility()
    logger.info("")
    check_bs4_compatibility()
    logger.info("")
    check_pandas_compatibility()
    
    logger.info("\nCheck complete!")

if __name__ == "__main__":
    main()