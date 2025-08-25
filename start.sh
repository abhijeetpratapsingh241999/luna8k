#!/bin/bash

echo "Phone-PC Sync Emulator Pro"
echo "==========================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Error: Python is not installed"
        echo "Please install Python 3.8 or higher"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Starting Phone-PC Sync Emulator Launcher..."
echo

# Start the launcher
$PYTHON_CMD launcher.py

echo
echo "Application closed."
read -p "Press Enter to continue..."