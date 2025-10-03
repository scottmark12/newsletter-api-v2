#!/usr/bin/env python3
"""
Ultra-minimal worker - just prints and waits
This will help us identify if the issue is with ANY imports at all
"""

print("=== MINIMAL WORKER STARTING ===")

# No imports at all - just basic Python
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

# Just a simple loop
counter = 0
while True:
    counter += 1
    print(f"Minimal worker heartbeat {counter}")
    
    # Sleep using time.sleep but import it inline
    try:
        import time
        time.sleep(60)
    except Exception as e:
        print(f"Error: {e}")
        break

print("Minimal worker stopped")
