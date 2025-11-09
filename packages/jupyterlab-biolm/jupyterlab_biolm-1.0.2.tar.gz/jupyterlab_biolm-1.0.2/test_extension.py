#!/usr/bin/env python3
"""Test script to verify BioLM JupyterLab extension installation"""

import sys
import os

def test_import():
    """Test that the extension module can be imported"""
    try:
        import jupyterlab_biolm
        print("✅ Extension module imports successfully")
        print(f"   Location: {jupyterlab_biolm.__file__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import extension: {e}")
        return False

def test_labextension_paths():
    """Test that labextension paths are defined"""
    try:
        from jupyterlab_biolm import _jupyter_labextension_paths
        paths = _jupyter_labextension_paths()
        print("✅ Labextension paths defined")
        print(f"   Paths: {paths}")
        if paths and len(paths) > 0:
            ext_path = paths[0]
            src = ext_path.get('src', '')
            dest = ext_path.get('dest', '')
            print(f"   Source: {src}, Destination: {dest}")
            
            # Check if source directory exists
            if os.path.exists(src):
                print(f"✅ Source directory exists: {src}")
                static_dir = os.path.join(src, 'static')
                if os.path.exists(static_dir):
                    files = os.listdir(static_dir)
                    print(f"✅ Static files found: {len(files)} files")
                    return True
                else:
                    print(f"⚠️  Static directory not found: {static_dir}")
            else:
                print(f"⚠️  Source directory not found: {src}")
        return True
    except Exception as e:
        print(f"❌ Failed to get labextension paths: {e}")
        return False

def test_extension_files():
    """Test that extension files exist"""
    ext_dir = "/Users/astewart/Library/Python/3.9/share/jupyter/labextensions/jupyterlab-biolm"
    if os.path.exists(ext_dir):
        print(f"✅ Extension directory exists: {ext_dir}")
        static_dir = os.path.join(ext_dir, "static")
        if os.path.exists(static_dir):
            files = os.listdir(static_dir)
            js_files = [f for f in files if f.endswith('.js')]
            print(f"✅ Static files: {len(files)} total, {len(js_files)} JS files")
            return True
        else:
            print(f"⚠️  Static directory not found")
    else:
        print(f"⚠️  Extension directory not found: {ext_dir}")
    return False

def main():
    print("=" * 60)
    print("BioLM JupyterLab Extension - Installation Test")
    print("=" * 60)
    print()
    
    results = []
    results.append(("Module Import", test_import()))
    print()
    results.append(("Labextension Paths", test_labextension_paths()))
    print()
    results.append(("Extension Files", test_extension_files()))
    print()
    
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Extension is properly installed.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
