#!/usr/bin/env python3
"""Wait for JupyterLab server to start and print URL"""
import urllib.request
import json
import glob
import os
import time

runtime_dir = os.path.expanduser("~/Library/Jupyter/runtime")
for i in range(10):
    files = glob.glob(os.path.join(runtime_dir, "*.json"))
    for f in files:
        try:
            with open(f) as fp:
                data = json.load(fp)
                if data.get('port') == 8889:
                    token = data.get('token')
                    print(f"\n✅ JupyterLab is running!")
                    print(f"🌐 URL: http://localhost:8889/lab?token={token}")
                    exit(0)
        except:
            pass
    time.sleep(1)
print("\n⚠️  Server may still be starting...")

