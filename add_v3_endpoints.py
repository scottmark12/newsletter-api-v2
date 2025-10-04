#!/usr/bin/env python3
"""
Simple script to add v3 endpoints to existing main.py
This allows you to use v3 features with your existing database setup
"""

import os

def add_v3_to_main():
    """Add v3 endpoints to existing main.py"""
    
    main_py_path = "app/main.py"
    
    if not os.path.exists(main_py_path):
        print("❌ main.py not found!")
        return False
    
    # Read the v3 endpoints
    with open("app/main_v3_endpoints.py", "r") as f:
        v3_content = f.read()
    
    # Extract the function definitions
    v3_function = v3_content.split("def add_v3_endpoints(web_app):")[1].strip()
    
    # Read existing main.py
    with open(main_py_path, "r") as f:
        main_content = f.read()
    
    # Check if v3 endpoints are already added
    if "add_v3_endpoints" in main_content:
        print("✅ V3 endpoints already added to main.py")
        return True
    
    # Add import and function call at the end
    v3_import = """
# V3 Theme-based endpoints
from .main_v3_endpoints import add_v3_endpoints

# Add v3 endpoints to the app
add_v3_endpoints(web_app)
"""
    
    # Add to the end of main.py
    new_content = main_content + v3_import
    
    # Write back to main.py
    with open(main_py_path, "w") as f:
        f.write(new_content)
    
    print("✅ V3 endpoints added to main.py successfully!")
    return True

if __name__ == "__main__":
    add_v3_to_main()
