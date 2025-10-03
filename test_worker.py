#!/usr/bin/env python3
"""
Test worker that explicitly avoids any auto-detection issues
"""
print("TEST WORKER STARTING")
print("This is a test worker to debug Render issues")

# Basic imports only
import os
import sys

print(f"Python: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Check environment
print("Environment variables:")
for key in ['DATABASE_URL', 'FORCE_SQLITE', 'PYTHONPATH', 'PYTHON']:
    value = os.environ.get(key, 'NOT SET')
    print(f"  {key}: {value}")

print("TEST WORKER RUNNING - NO IMPORTS BEYOND OS/SYS")
print("If you see this, the basic worker works!")

# Simple counter
count = 0
while True:
    count += 1
    print(f"Test worker running... iteration {count}")
    
    # Use inline import to avoid any import issues
    try:
        import time
        time.sleep(30)  # Check every 30 seconds
    except Exception as e:
        print(f"Sleep error: {e}")
        break

print("TEST WORKER STOPPED")