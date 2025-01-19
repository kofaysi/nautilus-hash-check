#!/bin/bash

# Uninstall the Nautilus Hash Check Extension

EXT_DIR="$HOME/.local/share/nautilus-python/extensions"
EMBLEMS_DIR="$HOME/.icons/hicolor/48x48/emblems"
ICONS_DIR="$HOME/.icons"


# Remove the extension script
if [ -f "$EXT_DIR/hash_check_emblem.py" ]; then
    echo "Removing Nautilus Hash Check script..."
    rm -f "$EXT_DIR/hash_check_emblem.py"
else
    echo "Nautilus Hash Check script not found in $EXT_DIR."
fi

# Remove the emblem files
if [ -f "$EMBLEMS_DIR/emblem-hash-verified.png" ]; then
    echo "Removing emblem-hash-verified PNG..."
    rm -f "$EMBLEMS_DIR/emblem-hash-verified.png"
fi

if [ -f "$EMBLEMS_DIR/emblem-hash-verified.icon" ]; then
    echo "Removing emblem-hash-verified ICON..."
    rm -f "$EMBLEMS_DIR/emblem-hash-verified.icon"
fi

if [ -f "$EMBLEMS_DIR/emblem-hash-verified.png" ]; then
    echo "Removing emblem-hash-verified PNG..."
    rm -f "$EMBLEMS_DIR/emblem-hash-verified.png"
fi

if [ -f "$EMBLEMS_DIR/emblem-hash-verified.icon" ]; then
    echo "Removing emblem-hash-verified ICON..."
    rm -f "$EMBLEMS_DIR/emblem-hash-verified.icon"
fi

# Recursive cleanup of empty directories
cleanup_empty_dirs() {
    for dir in "$@"; do
        find "$dir" -depth -type d -empty -delete
    done
}

echo "Cleaning up empty directories..."
cleanup_empty_dirs "$EXT_DIR" "$ICONS_DIR"
echo "Empty directories cleaned up."

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
