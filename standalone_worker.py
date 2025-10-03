#!/usr/bin/env python3
"""
Standalone worker that explicitly sets up the environment
"""
import sys
import os

# Explicitly set up the environment to avoid any auto-detection
print("=== STANDALONE WORKER STARTING ===")

# Clear any problematic environment variables
for key in list(os.environ.keys()):
    if 'application' in key.lower() or 'app' in key.lower():
        print(f"Removing environment variable: {key}")
        del os.environ[key]

# Set explicit Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'app'))

print(f"Python version: {sys.version}")
print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path}")

# Let the environment variables from render.yaml handle database configuration
# Remove any SQLite overrides
if 'FORCE_SQLITE' in os.environ:
    del os.environ['FORCE_SQLITE']

print("Environment setup complete")
print("Starting worker loop...")

# Simple worker loop
count = 0
while True:
    count += 1
    print(f"Standalone worker heartbeat {count}")
    
    try:
        import time
        time.sleep(60)
    except KeyboardInterrupt:
        print("Worker stopped by user")
        break
    except Exception as e:
        print(f"Error: {e}")
        break

print("Standalone worker stopped")
