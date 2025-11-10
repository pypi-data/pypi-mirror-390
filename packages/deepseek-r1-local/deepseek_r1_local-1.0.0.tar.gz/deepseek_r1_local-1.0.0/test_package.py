#!/usr/bin/env python3
"""
Quick test to verify package is properly structured
"""
import sys

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    try:
        from deepseek_r1_local import __version__
        print(f"✓ Package version: {__version__}")
        
        from deepseek_r1_local import app
        print("✓ Flask app imported")
        
        from deepseek_r1_local import ModelManager
        print("✓ ModelManager imported")
        
        from deepseek_r1_local import Council
        print("✓ Council imported")
        
        from deepseek_r1_local import WebSearcher
        print("✓ WebSearcher imported")
        
        from deepseek_r1_local.cli import main
        print("✓ CLI imported")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_structure():
    """Test package structure"""
    print("\nTesting package structure...")
    import os
    from pathlib import Path
    
    base = Path("deepseek_r1_local")
    
    files = [
        base / "__init__.py",
        base / "app.py",
        base / "cli.py",
        base / "templates" / "index.html",
    ]
    
    for f in files:
        if f.exists():
            print(f"✓ {f}")
        else:
            print(f"✗ Missing: {f}")
            return False
    
    return True

def test_config_files():
    """Test configuration files exist"""
    print("\nTesting configuration files...")
    from pathlib import Path
    
    files = [
        "setup.py",
        "pyproject.toml",
        "requirements.txt",
        "README.md",
        "LICENSE",
        "MANIFEST.in",
    ]
    
    for f in files:
        if Path(f).exists():
            print(f"✓ {f}")
        else:
            print(f"✗ Missing: {f}")
            return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("DeepSeek R1 Local - Package Test")
    print("=" * 60)
    print()
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Structure", test_structure()))
    results.append(("Config Files", test_config_files()))
    
    print()
    print("=" * 60)
    print("Test Results")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:20s} {status}")
    
    all_passed = all(r for _, r in results)
    
    print()
    if all_passed:
        print("🎉 All tests passed!")
        print()
        print("Next steps:")
        print("  1. pip install -e .")
        print("  2. deepseek-r1-local download-model")
        print("  3. deepseek-r1-local start")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
