import os
import time
import hashlib
import threading
import subprocess  # To run gio commands
import gi  # Import gi for specifying the Nautilus version

gi.require_version('Nautilus', '3.0')
from gi.repository import Nautilus, GObject

# Supported hash file extensions
HASH_FILE_EXTENSIONS = [".md5sum", ".sha256sum"]
DEBUG_FILE = "/tmp/debug_output.txt"
VERIFICATION_CACHE = {}  # Cache: {file_path: last_verification_time}

# Name of the emblem to apply
EMBLEM_NAME = "emblem-shield"

def log_debug_message(folder_path, message):
    """Log debug messages to a global debug file with timestamps."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(DEBUG_FILE, "a") as f:
        f.write(f"[{timestamp}] {folder_path}: {message}\n")

def is_emblem_applied(file_path, emblem_name):
    """Check if the specified emblem is already applied to the file."""
    log_debug_message(os.path.dirname(file_path), f"Checking if emblem '{emblem_name}' is already applied for: {file_path}")
    try:
        result = subprocess.run(
            ["gio", "info", "-a", "metadata::emblems", file_path],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        )
        for line in result.stdout.splitlines():
            if ": " in line and line.lstrip().startswith("metadata::emblems:"):
                emblems = line.split(": ", 1)[1].strip().strip("[]").split(", ")
                if emblem_name in emblems:
                    log_debug_message(os.path.dirname(file_path), f"Emblem '{emblem_name}' is already applied for: {file_path}")
                    return True
        log_debug_message(os.path.dirname(file_path), f"Emblem '{emblem_name}' is NOT applied for: {file_path}")
    except subprocess.CalledProcessError as e:
        log_debug_message(os.path.dirname(file_path), f"Error checking emblem for {file_path}: {e}")
    return False

def apply_emblem(file_path):
    """Apply an emblem to the file if not already applied."""
    if is_emblem_applied(file_path, EMBLEM_NAME):
        log_debug_message(os.path.dirname(file_path), f"Skipping emblem application for: {file_path} as it is already applied.")
        return
    try:
        log_debug_message(os.path.dirname(file_path), f"Applying emblem '{EMBLEM_NAME}' for: {file_path}")
        subprocess.run(
            ["gio", "set", "-t", "stringv", file_path, "metadata::emblems", EMBLEM_NAME],
            check=True,
        )
        log_debug_message(os.path.dirname(file_path), f"Successfully applied emblem '{EMBLEM_NAME}' for: {file_path}")
    except subprocess.CalledProcessError as e:
        log_debug_message(os.path.dirname(file_path), f"Error applying emblem for {file_path}: {e}")

def validate_file_hash(file_path, hash_file, debug_folder):
    """Validate the file's hash against the hash file."""
    try:
        log_debug_message(debug_folder, f"Starting validation of {file_path} against {hash_file}")
        with open(hash_file, "r") as f:
            for line in f:
                hash_value, file_name = line.strip().split("  ", 1)
                if os.path.basename(file_path) == file_name:
                    # Determine the hash function
                    if hash_file.endswith(".md5sum"):
                        hash_func = hashlib.md5
                    elif hash_file.endswith(".sha256sum"):
                        hash_func = hashlib.sha256
                    else:
                        log_debug_message(debug_folder, f"Unsupported hash type in {hash_file}")
                        return False

                    # Calculate the file's hash
                    log_debug_message(debug_folder, f"Calculating hash for {file_path}")
                    with open(file_path, "rb") as file_to_check:
                        file_hash = hash_func(file_to_check.read()).hexdigest()

                    if file_hash == hash_value:
                        log_debug_message(debug_folder, f"File verified: {file_path} with {os.path.basename(hash_file)}")
                        return True
                    else:
                        log_debug_message(debug_folder, f"Hash mismatch for file: {file_path}")
    except Exception as e:
        log_debug_message(debug_folder, f"Error validating {file_path}: {e}")
    return False

class HashOverlayProvider(GObject.GObject, Nautilus.InfoProvider):
    def update_file_info(self, file):
        """Add an emblem for files with verified hashes."""
        if file.get_uri_scheme() != "file":
            return

        file_path = file.get_location().get_path()

        # Ignore directories and known hash files
        if not os.path.isfile(file_path):
            log_debug_message(file_path, "Ignored: Not a file")
            return
        if any(file_path.endswith(ext) for ext in HASH_FILE_EXTENSIONS):
            log_debug_message(file_path, "Ignored: Hash file")
            return

        folder_path = os.path.dirname(file_path)

        # Avoid redundant processing
        current_time = time.time()
        last_verified = VERIFICATION_CACHE.get(file_path, 0)
        if current_time - last_verified < 10:  # Skip if verified in the last 10 seconds
            log_debug_message(folder_path, f"Skipped: Recently verified {file_path}")
            return

        # Check if emblem is already applied
        if is_emblem_applied(file_path, EMBLEM_NAME):
            log_debug_message(folder_path, f"Emblem already applied for: {file_path}")
            return

        # Run hash validation in a separate thread
        def validate_and_update():
            log_debug_message(folder_path, f"Starting hash validation thread for {file_path}")
            for hash_ext in HASH_FILE_EXTENSIONS:
                hash_file = os.path.join(folder_path, f"{os.path.basename(file_path)}{hash_ext}")
                if os.path.exists(hash_file):
                    if validate_file_hash(file_path, hash_file, folder_path):
                        VERIFICATION_CACHE[file_path] = time.time()
                        apply_emblem(file_path)
                        return

            log_debug_message(folder_path, f"No matching hash file found for: {file_path}")

        threading.Thread(target=validate_and_update, daemon=True).start()
