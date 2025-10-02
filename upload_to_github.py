#!/usr/bin/env python3
"""
Quick script to upload all files to GitHub using the GitHub API
"""
import os
import base64
import requests
import json
from pathlib import Path

# Configuration
GITHUB_USERNAME = "scottmark12"
REPO_NAME = "newsletter-api-v2"
GITHUB_TOKEN = input("Enter your GitHub Personal Access Token: ")

# Files to ignore (same as .gitignore)
IGNORE_PATTERNS = {
    '.env', 'newsletter.db', '__pycache__', '.git', 'venv', '.DS_Store',
    '*.pyc', '*.log', '*.sqlite', '*.sqlite3'
}

def should_ignore(file_path):
    """Check if file should be ignored"""
    path_str = str(file_path)
    for pattern in IGNORE_PATTERNS:
        if pattern in path_str or file_path.name.startswith('.'):
            return True
    return False

def upload_file(file_path, content, github_path):
    """Upload a single file to GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{github_path}"
    
    # Encode content as base64
    content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    data = {
        "message": f"Add {github_path}",
        "content": content_b64,
        "branch": "main"
    }
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.put(url, json=data, headers=headers)
    
    if response.status_code in [200, 201]:
        print(f"✅ Uploaded: {github_path}")
        return True
    else:
        print(f"❌ Failed to upload {github_path}: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def main():
    """Main upload function"""
    print("🚀 Uploading Newsletter API v2 to GitHub...")
    print(f"📍 Repository: {GITHUB_USERNAME}/{REPO_NAME}")
    print()
    
    # Get all files in current directory
    current_dir = Path(".")
    all_files = []
    
    for root, dirs, files in os.walk(current_dir):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if not should_ignore(Path(root) / d)]
        
        for file in files:
            file_path = Path(root) / file
            if not should_ignore(file_path):
                all_files.append(file_path)
    
    print(f"📁 Found {len(all_files)} files to upload")
    print()
    
    # Upload each file
    success_count = 0
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert to GitHub path (use forward slashes)
            github_path = str(file_path).replace('\\', '/').lstrip('./')
            
            if upload_file(file_path, content, github_path):
                success_count += 1
                
        except UnicodeDecodeError:
            print(f"⚠️  Skipping binary file: {file_path}")
        except Exception as e:
            print(f"❌ Error with {file_path}: {e}")
    
    print()
    print(f"🎉 Upload complete! {success_count}/{len(all_files)} files uploaded")
    print(f"🌐 View your repo: https://github.com/{GITHUB_USERNAME}/{REPO_NAME}")

if __name__ == "__main__":
    main()
