#!/usr/bin/env python3
"""Check if a specific package version exists on PyPI."""
import sys
import requests

def check_package_exists(package_name, version):
    try:
        response = requests.get(f'https://pypi.org/pypi/{package_name}/{version}/json', timeout=10)
        if response.status_code == 200:
            print('✅ Package found on PyPI')
            return True
        else:
            print(f'❌ Package not found: HTTP {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: check-pypi-package.py <package_name> <version>')
        sys.exit(1)
    
    package_name = sys.argv[1]
    version = sys.argv[2]
    exists = check_package_exists(package_name, version)
    sys.exit(0 if exists else 1)