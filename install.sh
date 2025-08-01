#!/bin/bash
# Simple installation script for ApplerGUI

echo "🍎 Installing ApplerGUI..."

# Install the package
pip3 install --user .

# Check if installation was successful
if command -v applergui &> /dev/null; then
    echo "✅ ApplerGUI installed successfully!"
    echo "▶️ Run with: applergui"
else
    echo "⚠️ Command not found in PATH. Try:"
    echo "   ~/.local/bin/applergui"
fi