"""Simple PyPI upload script to avoid encoding issues"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

import requests
from pathlib import Path

# Configuration
token = "pypi-AgEIcHlwaS5vcmcCJDJjZTAyYzE2LWM1NTUtNGUyNS04ZjU3LWE2YjBmZjA4MmFlOQACKlszLCJhY2Y0NzgwZS1iYjU4LTRlMjctYTNiYS1jMGIwYjA4NmM3MzgiXQAABiB-NNtO-2YRcj1S9_pd-8GWsELieO4KIDmIsDXbaoDI7A"
dist_dir = Path("dist")

# Find files
files = list(dist_dir.glob("*.whl")) + list(dist_dir.glob("*.tar.gz"))

for file in files:
    print(f"Uploading {file.name}...")

    with open(file, 'rb') as f:
        response = requests.post(
            "https://upload.pypi.org/legacy/",
            auth=("__token__", token),
            files={'content': (file.name, f, 'application/octet-stream')},
            data={
                ':action': 'file_upload',
                'protocol_version': '1'
            }
        )

    if response.status_code == 200:
        print(f"Successfully uploaded {file.name}")
    else:
        print(f"Failed to upload {file.name}: {response.status_code}")
        print(response.text)

print("\nDone!")
