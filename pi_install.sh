#!/bin/bash

# pi_install.sh

set -e

# Update and Upgrade the Pi, just in case
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Python3 if not already installed
if ! command -v python3 &>/dev/null; then
    echo "Python 3 is not installed. Installing Python 3..."
    sudo apt-get install -y python3
else
    echo "Python 3 is already installed."
fi

# Install pip for Python 3 if not already installed
if ! command -v pip3 &>/dev/null; then
    echo "pip for Python 3 is not installed. Installing pip for Python 3..."
    sudo apt-get install -y python3-pip
else
    echo "pip for Python 3 is already installed."
fi

# Upgrade pip to the latest version
echo "Upgrading pip..."
pip3 install --upgrade pip

# Check if the .venv directory exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment
echo "Activating the virtual environment..."
source .venv/bin/activate

echo "Virtual environment activated. You are now using Python and pip from within the virtual environment."

# Reminder to deactivate when done
echo "Remember to run 'deactivate' when you are done using the virtual environment."

echo $VIRTUAL_ENV

pip install -r requirements.txt
pip install dbus_next
