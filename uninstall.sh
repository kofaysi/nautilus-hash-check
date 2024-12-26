#!/bin/bash

# Uninstall the Nautilus Hash Check Extension

EXT_DIR="$HOME/.local/share/nautilus-python/extensions"
ICON_DIR="$HOME/.icons/hicolor/48x48/emblems"

# Remove the extension script
if [ -f "$EXT_DIR/nautilus_hash_check.py" ]; then
    echo "Removing Nautilus Hash Check script..."
    rm -f "$EXT_DIR/nautilus_hash_check.py"
else
    echo "Nautilus Hash Check script not found in $EXT_DIR."
fi

# Remove the emblem files
if [ -f "$ICON_DIR/emblem-shield.png" ]; then
    echo "Removing emblem PNG..."
    rm -f "$ICON_DIR/emblem-shield.png"
fi

if [ -f "$ICON_DIR/emblem-shield.icon" ]; then
    echo "Removing emblem ICON..."
    rm -f "$ICON_DIR/emblem-shield.icon"
fi

# Update the icon cache
if [ -d "$HOME/.icons" ]; then
    echo "Updating icon cache..."
    gtk-update-icon-cache "$HOME/.icons"
else
    echo "Icon directory not found. Skipping icon cache update."
fi

# Notify the user
echo "Uninstallation complete. Please restart Nautilus if it is running."

