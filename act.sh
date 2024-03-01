#!/bin/bash

# Check if the virtual environment directory exists
if [ -d ".venv" ]; then
    # Activate the virtual environment
    source .venv/bin/activate

    pip install --upgrade pip

    # Check if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        # Install dependencies from requirements.txt
        pip install -r requirements.txt
        pip install dbus_next

    else
        echo "requirements.txt not found"
    fi
else
    echo ".venv directory does not exist"
fi
