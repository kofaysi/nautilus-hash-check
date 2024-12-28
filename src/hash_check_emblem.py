import os
import hashlib
import threading
import subprocess
import gi

gi.require_version('Nautilus', '3.0')
from gi.repository import Nautilus, GObject

# Supported hash file extensions
HASH_FILE_EXTENSIONS = [".md5sum", ".sha1sum", ".sha256sum", ".sha512sum"]

# Map hash cores to their corresponding hashlib functions
HASH_FUNCTIONS = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
}

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

def calculate_file_hash(file_path, hash_function):
    """Calculate the hash of a file using the specified hash function."""
    with open(file_path, "rb") as f:
        file_hash = hash_function(f.read()).hexdigest()
    return file_hash

def get_hash_function(hash_file_extension):
    """Retrieve the hash function based on the hash file extension."""
    # Strip the ".sum" suffix to get the hash core (e.g., "md5", "sha1")
    hash_core = hash_file_extension.lstrip(".").replace("sum", "")
    return HASH_FUNCTIONS.get(hash_core)

def is_emblem_applied(file_path, emblem_name):
    """Check if the specified emblem is already applied to the file."""
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
                    return True
    except subprocess.CalledProcessError as e:
        log_debug_message(os.path.dirname(file_path), f"Error checking emblem for {file_path}: {e}")
    return False

def validate_file(file_path, hash_file, debug_folder):
    """Validate the file's hash against the hash file."""
    try:
        log_debug_message(debug_folder, f"Validating {file_path} using {hash_file}")
        with open(hash_file, "r") as f:
            for line in f:
                try:
                    hash_value, file_name = line.strip().split("  ", 1)
                    if os.path.basename(file_path) == file_name:
                        # Determine the hash function dynamically
                        hash_func = get_hash_function(os.path.splitext(hash_file)[1])
                        if not hash_func:
                            log_debug_message(debug_folder, f"Unsupported hash type in {hash_file}")
                            return False

                        # Calculate and compare hash
                        calculated_hash = calculate_file_hash(file_path, hash_func)
                        if calculated_hash == hash_value:
                            log_debug_message(debug_folder, f"Hash validated for {file_path}")
                            return True
                        else:
                            log_debug_message(debug_folder, f"Hash mismatch for {file_path}")
                except ValueError:
                    log_debug_message(debug_folder, f"Malformed line in {hash_file}: {line.strip()}")
    except Exception as e:
        log_debug_message(debug_folder, f"Error validating {file_path}: {e}")
    return False

def apply_emblem(file_path):
    """Apply an emblem to the file."""
    try:
        log_debug_message(os.path.dirname(file_path), f"Applying emblem '{EMBLEM_NAME}' to {file_path}")
        subprocess.run(
            ["gio", "set", "-t", "stringv", file_path, "metadata::emblems", EMBLEM_NAME],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        log_debug_message(os.path.dirname(file_path), f"Error applying emblem to {file_path}: {e}")

class HashOverlayProvider(GObject.GObject, Nautilus.InfoProvider):
    def update_file_info(self, file):
        """Update file info in Nautilus."""
        if file.get_uri_scheme() != "file":
            return

        file_path = file.get_location().get_path()

        # Ignore non-hash files
        if not any(file_path.endswith(ext) for ext in HASH_FILE_EXTENSIONS):
            return

        folder_path = os.path.dirname(file_path)

        # Run hash validation in a separate thread
        def validate_and_process():
            log_debug_message(folder_path, f"Processing hash file: {file_path}")
            with open(file_path, "r") as f:
                for line in f:
                    try:
                        hash_value, target_filename = line.strip().split("  ", 1)
                        target_file_path = os.path.join(folder_path, target_filename)

                        if os.path.exists(target_file_path):
                            # Skip files that already have the emblem
                            if is_emblem_applied(target_file_path, EMBLEM_NAME):
                                log_debug_message(folder_path, f"Skipping {target_file_path} (emblem already applied)")
                                continue

                            if validate_file(target_file_path, file_path, folder_path):
                                apply_emblem(target_file_path)
                        else:
                            log_debug_message(folder_path, f"Target file not found: {target_filename}")
                    except ValueError:
                        log_debug_message(folder_path, f"Malformed line in {file_path}: {line.strip()}")

        threading.Thread(target=validate_and_process, daemon=True).start()