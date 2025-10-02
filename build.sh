#!/bin/bash

# Force Python 3.11 installation and usage
echo "=== FORCING PYTHON 3.11 INSTALLATION ==="

# Update package lists
apt-get update

# Install Python 3.11 and related packages
echo "Installing Python 3.11..."
apt-get install -y python3.11 python3.11-pip python3.11-venv python3.11-dev

# Create symlinks to make python3.11 the default python3
ln -sf /usr/bin/python3.11 /usr/bin/python3
ln -sf /usr/bin/python3.11 /usr/bin/python

# Verify Python version
echo "Python version after installation:"
python --version
python3 --version
python3.11 --version

# Install pip for Python 3.11
python3.11 -m ensurepip --upgrade

# Install requirements using Python 3.11
echo "Installing Python packages with Python 3.11..."
python3.11 -m pip install --upgrade pip
python3.11 -m pip install -r requirements.txt

echo "=== BUILD COMPLETE WITH PYTHON 3.11 ==="