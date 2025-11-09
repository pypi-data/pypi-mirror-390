#!/usr/bin/env python3
"""Check server extension status in running JupyterLab"""
import urllib.request
import json
import glob
import os

runtime_dir = os.path.expanduser("~/Library/Jupyter/runtime")
files = glob.glob(os.path.join(runtime_dir, "*.json"))
token = None
for f in files:
    try:
        with open(f) as fp:
            data = json.load(fp)
            if data.get('port') == 8889:
                token = data.get('token')
                break
    except:
        pass

if not token:
    print("❌ JupyterLab not running on port 8889")
    exit(1)

# Test endpoint
try:
    url = f"http://localhost:8889/biolm/api/models?token={token}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=2) as response:
        print("✅ Server extension is loaded and responding")
except urllib.error.HTTPError as e:
    if e.code == 404:
        print("❌ Server extension endpoint not found (404)")
    else:
        print(f"⚠️  HTTP {e.code} (endpoint exists but returned error)")
except Exception as e:
    print(f"❌ Error: {e}")

