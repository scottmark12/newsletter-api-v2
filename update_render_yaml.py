#!/usr/bin/env python3
"""
Quick script to update just the render.yaml file on GitHub
"""
import requests
import base64
import json

# Your GitHub info
GITHUB_USERNAME = "scottmark12"
REPO_NAME = "newsletter-api-v2"
GITHUB_TOKEN = "ghp_XZfzWvnpGvwOvZNYlDxSMGjYHRNnxH1rUYqF"  # Replace with your token

def update_render_yaml():
    # Read the local render.yaml
    with open("render.yaml", "r") as f:
        content = f.read()
    
    # GitHub API URL
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/render.yaml"
    
    # Get current file SHA (needed for updates)
    response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    if response.status_code == 200:
        current_sha = response.json()["sha"]
    else:
        print(f"Error getting current file: {response.status_code}")
        return
    
    # Encode content
    content_encoded = base64.b64encode(content.encode()).decode()
    
    # Update file
    data = {
        "message": "Fix DATABASE_URL in render.yaml",
        "content": content_encoded,
        "sha": current_sha
    }
    
    response = requests.put(url, json=data, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    
    if response.status_code == 200:
        print("✅ render.yaml updated successfully!")
    else:
        print(f"❌ Error updating file: {response.status_code}")
        print(response.json())

if __name__ == "__main__":
    update_render_yaml()
