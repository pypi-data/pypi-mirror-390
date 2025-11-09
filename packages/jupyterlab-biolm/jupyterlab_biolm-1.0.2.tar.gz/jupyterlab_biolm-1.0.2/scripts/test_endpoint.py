#!/usr/bin/env python3
"""Test the server proxy endpoint"""
import urllib.request
import json
import glob
import os

# Find runtime file
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

try:
    url = f"http://localhost:8889/biolm/api/models?token={token}"
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    with urllib.request.urlopen(req, timeout=3) as response:
        data = json.loads(response.read().decode('utf-8'))
        print("✅✅✅ Server extension endpoint is WORKING!")
        print(f"   Response type: {type(data).__name__}")
        if isinstance(data, list):
            print(f"   Models returned: {len(data)}")
except urllib.error.HTTPError as e:
    if e.code == 401 or e.code == 403:
        print("✅ Server extension loaded (auth required)")
    elif e.code == 404:
        print("❌ Endpoint not found (404) - server extension may not be loaded")
    else:
        print(f"⚠️  HTTP {e.code}: {e.reason}")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

