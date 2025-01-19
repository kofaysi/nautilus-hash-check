#!/bin/bash

echo "Installing Nautilus Hash Check Extension..."

# Install Python packages
echo "Installing Python dependencies..."
pip3 install --user -r requirements.txt

# Copy the script to the Nautilus extensions directory
EXT_DIR="$HOME/.local/share/nautilus-python/extensions"
mkdir -p "$EXT_DIR"
cp src/hash_check_emblem.py "$EXT_DIR"

# Copy the emblem files to the local icons directory
ICON_DIR="$HOME/.icons/hicolor/48x48/emblems"
mkdir -p "$ICON_DIR"
cp assets/emblem-hash-verified.png "$ICON_DIR"
cp assets/emblem-hash-verified.icon "$ICON_DIR"
cp assets/emblem-hash-error.png "$ICON_DIR"
cp assets/emblem-hash-error.icon "$ICON_DIR"

# Update the icon cache
echo "Updating icon cache..."
gtk-update-icon-cache "$HOME/.icons"

echo "Installation complete. Restart Nautilus to activate the extension."

# Prompt the user to restart Nautilus
read -p "Do you want to restart Nautilus now? [Y/n] " response
response=${response,,}  # Convert to lowercase

if [[ "$response" == "y" || "$response" == "" ]]; then
    echo "Restarting Nautilus..."
    pkill nautilus
    nohup nautilus >/dev/null 2>&1 &
    echo "Nautilus has been restarted."
else
    echo "Please restart Nautilus manually to activate the extension."
fi
