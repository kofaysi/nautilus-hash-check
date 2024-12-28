#!/bin/bash

# Uninstall the Nautilus Hash Check Extension

EXT_DIR="$HOME/.local/share/nautilus-python/extensions"
ICON_DIR="$HOME/.icons/hicolor/48x48/emblems"

# Remove the extension script
if [ -f "$EXT_DIR/hash_check_emblem.py" ]; then
    echo "Removing Nautilus Hash Check script..."
    rm -f "$EXT_DIR/hash_check_emblem.py"
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

# Remove the directories if they are empty (including all empty parent directories)
echo "Cleaning up empty directories..."
find "$EXT_DIR" "$ICON_DIR" -type d -empty -delete 2>/dev/null

# Update the icon cache
if [ -d "$HOME/.icons" ]; then
    echo "Updating icon cache..."
    gtk-update-icon-cache "$HOME/.icons"
else
    echo "Icon directory not found. Skipping icon cache update."
fi

# Notify the user
echo "Uninstallation complete. Please restart Nautilus if it is running."

# Prompt the user to restart Nautilus
read -p "Do you want to restart Nautilus now? [Y/n] " response
response=${response,,}  # Convert to lowercase

if [[ "$response" == "y" || "$response" == "" ]]; then
    echo "Restarting Nautilus..."
    pkill nautilus
    nohup nautilus >/dev/null 2>&1 &
    echo "Nautilus has been restarted."
else
    echo "Please restart Nautilus manually to finalize the uninstallation."
fi
