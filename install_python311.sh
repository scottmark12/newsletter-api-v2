#!/bin/bash

# Force install Python 3.11 on Render
echo "=== FORCING PYTHON 3.11 INSTALLATION ==="

# Check current Python version
echo "Current Python version:"
python --version
python3 --version

# Install Python 3.11 if not available
if ! command -v python3.11 &> /dev/null; then
    echo "Installing Python 3.11..."
    sudo apt-get update
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
    sudo apt-get install -y python3.11-distutils
fi

# Create symlinks to ensure python3.11 is available
sudo ln -sf /usr/bin/python3.11 /usr/local/bin/python3.11
sudo ln -sf /usr/bin/python3.11 /usr/local/bin/python

# Verify installation
echo "Python 3.11 version:"
python3.11 --version

# Install pip for Python 3.11
curl https://bootstrap.pypa.io/get-pip.py | python3.11

echo "=== PYTHON 3.11 INSTALLATION COMPLETE ==="


