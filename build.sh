#!/bin/bash

echo "=== Starting build process ==="

# Check Python version
echo "Current Python version:"
python3 --version

# Create virtual environment to avoid system package conflicts
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip in virtual environment
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements in virtual environment
echo "Installing requirements..."
pip install -r requirements.txt

echo "=== Build complete ==="

# List installed packages for verification
echo "Installed packages:"
pip list | grep -E "(psycopg2|fastapi|uvicorn|sqlalchemy)"