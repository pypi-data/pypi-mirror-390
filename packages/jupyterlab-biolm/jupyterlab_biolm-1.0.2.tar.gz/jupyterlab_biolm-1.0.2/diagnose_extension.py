#!/usr/bin/env python3
"""Diagnostic script for BioLM extension issues"""

import json
import urllib.request
import urllib.error
import os

print("=" * 60)
print("BioLM Extension Diagnostic")
print("=" * 60)
print()

# 1. Check extension files
print("1. Extension Files:")
ext_dir = "/Users/astewart/Library/Python/3.9/share/jupyter/labextensions/jupyterlab-biolm"
if os.path.exists(ext_dir):
    print(f"   ✅ Extension directory exists: {ext_dir}")
    
    # Check package.json
    pkg_json = os.path.join(ext_dir, "package.json")
    if os.path.exists(pkg_json):
        with open(pkg_json) as f:
            pkg = json.load(f)
            print(f"   ✅ Package: {pkg.get('name')} v{pkg.get('version')}")
            
            # Check build config
            jlab = pkg.get('jupyterlab', {})
            build = jlab.get('_build', {})
            if build:
                print(f"   ✅ Build config found")
                print(f"      Load: {build.get('load')}")
                print(f"      Extension: {build.get('extension')}")
    else:
        print(f"   ❌ package.json not found")
    
    # Check static files
    static_dir = os.path.join(ext_dir, "static")
    if os.path.exists(static_dir):
        files = os.listdir(static_dir)
        js_files = [f for f in files if f.endswith('.js')]
        print(f"   ✅ Static files: {len(js_files)} JS files")
        
        # Check for remoteEntry
        remote_entry = [f for f in js_files if 'remoteEntry' in f]
        if remote_entry:
            print(f"   ✅ RemoteEntry found: {remote_entry[0]}")
        else:
            print(f"   ❌ RemoteEntry not found")
    else:
        print(f"   ❌ Static directory not found")
else:
    print(f"   ❌ Extension directory not found")

print()

# 2. Check JupyterLab API
print("2. JupyterLab Extension API:")
try:
    url = "http://localhost:8888/lab/api/extensions"
    req = urllib.request.Request(url)
    req.add_header('Authorization', 'token 25bb36b8f7cc3955b6cd5874962ac6371ad016d4a4c99c5a')
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        biolm = [e for e in data if 'biolm' in e.get('name', '').lower()]
        if biolm:
            ext = biolm[0]
            print(f"   ✅ Extension registered: {ext.get('name')}")
            print(f"      Enabled: {ext.get('enabled')}")
            print(f"      Status: {ext.get('status')}")
            print(f"      Installed: {ext.get('installed')}")
            print(f"      Version: {ext.get('installed_version')}")
        else:
            print(f"   ❌ Extension not found in API")
            print(f"      Total extensions: {len(data)}")
except Exception as e:
    print(f"   ⚠️  Could not check API: {e}")

print()

# 3. Check Python package
print("3. Python Package:")
try:
    import jupyterlab_biolm
    print(f"   ✅ Module imports: {jupyterlab_biolm.__file__}")
    
    from jupyterlab_biolm import _jupyter_labextension_paths
    paths = _jupyter_labextension_paths()
    print(f"   ✅ Labextension paths function works")
    print(f"      Paths: {paths}")
except Exception as e:
    print(f"   ❌ Python package issue: {e}")

print()
print("=" * 60)
print("Diagnostic Complete")
print("=" * 60)
print()
print("Next steps:")
print("1. Open browser console (F12) and check for errors")
print("2. Look for 'JupyterLab extension jupyterlab-biolm is activated!' message")
print("3. Check if BioLM icon appears in left sidebar")
print("4. If icon missing, check browser console for React/rendering errors")
