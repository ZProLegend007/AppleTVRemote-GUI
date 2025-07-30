#!/usr/bin/env python3
"""
Comprehensive dependency checker for ApplerGUI
Scans all Python files and identifies required packages
"""

import os
import ast
import sys
from pathlib import Path
from typing import Set, List, Dict

def find_python_files(directory: str) -> List[Path]:
    """Find all Python files in directory"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    return python_files

def extract_imports(file_path: Path) -> Set[str]:
    """Extract import statements from Python file"""
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
    
    except Exception as e:
        print(f"Warning: Could not parse {file_path}: {e}")
    
    return imports

def get_package_mapping() -> Dict[str, str]:
    """Map import names to pip package names"""
    return {
        'PIL': 'Pillow',
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
        'requests': 'requests',
        'aiohttp': 'aiohttp',
        'asyncio': '',  # Built-in
        'json': '',     # Built-in
        'os': '',       # Built-in
        'sys': '',      # Built-in
        'pathlib': '',  # Built-in
        'typing': '',   # Built-in
        'logging': '',  # Built-in
        'base64': '',   # Built-in
        'traceback': '',# Built-in
        'io': '',       # Built-in
        'signal': '',   # Built-in
        'PyQt6': 'PyQt6',
        'qasync': 'qasync',
        'pyatv': 'pyatv',
        'keyring': 'keyring',
        'cryptography': 'cryptography',
        'protobuf': 'protobuf',
        'setuptools': 'setuptools',
        # Local modules (no pip package needed)
        'ui': '',
        'backend': '',
    }

def main():
    """Main dependency checker"""
    print("🔍 ApplerGUI Dependency Checker")
    print("=" * 50)
    
    # Find all Python files
    current_dir = Path('.')
    python_files = find_python_files('.')
    
    print(f"📁 Found {len(python_files)} Python files")
    
    # Extract all imports
    all_imports = set()
    file_imports = {}
    
    for file_path in python_files:
        imports = extract_imports(file_path)
        all_imports.update(imports)
        file_imports[file_path] = imports
    
    # Map to package names
    package_mapping = get_package_mapping()
    required_packages = set()
    
    for import_name in all_imports:
        if import_name in package_mapping:
            package = package_mapping[import_name]
            if package:  # Skip built-in modules
                required_packages.add(package)
    
    print(f"\n📦 Required packages ({len(required_packages)}):")
    for package in sorted(required_packages):
        print(f"  - {package}")
    
    print(f"\n📄 Current requirements.txt should contain:")
    print("-" * 30)
    
    # Standard versions for common packages
    package_versions = {
        'PyQt6': '>=6.4.0',
        'PyQt6-Qt6': '>=6.4.0', 
        'PyQt6-tools': '>=6.4.0',
        'qasync': '>=0.24.1',
        'aiohttp': '>=3.8.0',
        'asyncio-mqtt': '>=0.11.0',
        'pyatv': '>=0.14.0',
        'Pillow': '>=9.0.0',
        'keyring': '>=24.0.0',
        'cryptography': '>=3.4.8',
        'protobuf': '>=3.19.0',
        'requests': '>=2.28.0',
        'setuptools': '>=65.0.0',
    }
    
    for package in sorted(required_packages):
        version = package_versions.get(package, '>=1.0.0')
        print(f"{package}{version}")
    
    print(f"\n🚨 Files with external imports:")
    for file_path, imports in file_imports.items():
        external_imports = [imp for imp in imports if imp in package_mapping and package_mapping[imp]]
        if external_imports:
            print(f"  {file_path}: {', '.join(external_imports)}")
    
    print(f"\n🔍 Import analysis summary:")
    print(f"  Total Python files: {len(python_files)}")
    print(f"  Unique imports found: {len(all_imports)}")
    print(f"  External packages needed: {len(required_packages)}")
    
    # Check for specific missing packages
    print(f"\n⚠️  Critical missing packages:")
    current_requirements = set()
    try:
        with open('requirements.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (before >= or == etc)
                    package_name = line.split('>=')[0].split('==')[0].split('<')[0].strip()
                    current_requirements.add(package_name)
    except FileNotFoundError:
        print("  No requirements.txt found!")
    
    missing_packages = required_packages - current_requirements
    if missing_packages:
        for package in sorted(missing_packages):
            print(f"  ❌ {package} - MISSING from requirements.txt")
    else:
        print("  ✅ All required packages are in requirements.txt")

if __name__ == "__main__":
    main()