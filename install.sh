#!/bin/bash

echo "Installing Nautilus Hash Check Extension..."

# Copy the script to the Nautilus extensions directory
EXT_DIR="$HOME/.local/share/nautilus-python/extensions"
mkdir -p "$EXT_DIR"
cp src/nautilus_hash_check.py "$EXT_DIR"

# Copy the emblem files to the local icons directory
ICON_DIR="$HOME/.icons/hicolor/48x48/emblems"
mkdir -p "$ICON_DIR"
cp assets/emblem-shield.png "$ICON_DIR"
cp assets/emblem-shield.icon "$ICON_DIR"

# Update the icon cache
echo "Updating icon cache..."
gtk-update-icon-cache "$HOME/.icons"

# installing python packages
pip3 install -r requirements.txt

echo "Installation complete. Restart Nautilus to activate the extension."
