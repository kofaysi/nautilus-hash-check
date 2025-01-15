import os
import hashlib
import threading
import gi

gi.require_version('Nautilus', '3.0')
from gi.repository import Nautilus, GObject
from datetime import datetime

# Supported hash file extensions
HASH_FILE_EXTENSIONS = [".md5sum", ".sha1sum", ".sha256sum", ".sha512sum"]

# Map hash cores to their corresponding hashlib functions
HASH_FUNCTIONS = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
}

# Name of the emblems to apply
VERIFIED_EMBLEM = "emblem-hash-verified"
WRONG_EMBLEM = "emblem-hash-error"

# Define a unique debug file path based on the script name
SCRIPT_NAME = os.path.basename(__file__).replace('.py', '')
DEBUG_FILE = f"/tmp/{SCRIPT_NAME}_debug.log"

# Global flag to control debug logging
ENABLE_DEBUG_LOGGING = True  # Set to False to disable logging

# Dictionary to store checksum information
# Format: {file_path: [hash_value, hash_function]}
checksum_info = {}
checksum_lock = threading.Lock()

def log_debug_message(folder_path, message):
    """Log debug messages to a global debug file with timestamps if logging is enabled."""
    if not ENABLE_DEBUG_LOGGING:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(DEBUG_FILE, "a") as f:
        f.write(f"[{timestamp}] {folder_path}: {message}\n")

# Add a log message when the script is loaded
log_debug_message("Global", "HashOverlayProvider extension script loaded.")


def is_checksum(file):
    """Check if a file is a checksum file."""
    return any(file.get_name().endswith(ext) for ext in HASH_FILE_EXTENSIONS)

def has_emblem(file):
    """Check if a file already has an emblem."""
    emblems = file.get_string_attribute("metadata::emblems")
    return emblems and (VERIFIED_EMBLEM in emblems or WRONG_EMBLEM in emblems)

def parse_add_checksum_info(file):
    """Parse checksum files and add info to checksum_info."""
    folder_path = file.get_parent_uri().replace("file://", "")
    file_path = file.get_location().get_path()

    # Determine the hash function dynamically from the checksum extension
    ext = os.path.splitext(file.get_name())[1]
    hash_func = HASH_FUNCTIONS.get(ext.lstrip(".").replace("sum", ""))
    if not hash_func:
        log_debug_message(folder_path, f"Unsupported hash type for file: {file_path}")
        return

    try:
        with open(file_path, "r") as f:
            for line in f:
                try:
                    hash_value, target_file = line.strip().split("  ", 1)
                    target_path = os.path.join(folder_path, target_file)
                    with checksum_lock:
                        checksum_info[target_path] = [hash_value, hash_func]
                    log_debug_message(folder_path, f"Added checksum info for: {target_path}")
                except ValueError:
                    log_debug_message(folder_path, f"Malformed line in checksum file: {line.strip()}")
                    continue
    except Exception as e:
        log_debug_message(folder_path, f"Error parsing checksum file {file_path}: {e}")

def checksum_is_correct(file):
    """Verify if the checksum of the file matches the recorded checksum."""
    file_path = file.get_location().get_path()
    folder_path = os.path.dirname(file_path)

    log_debug_message(folder_path, f"Validating checksum for: {file_path}")

    with checksum_lock:
        hash_data = checksum_info.get(file_path)

    if not hash_data:
        return False

    hash_value, hash_func = hash_data

    try:
        with open(file_path, "rb") as f:
            calculated_hash = hash_func(f.read()).hexdigest()
        return calculated_hash == hash_value
    except Exception as e:
        folder_path = os.path.dirname(file_path)
        log_debug_message(folder_path, f"Error calculating checksum for {file_path}: {e}")
        return False

def update_cb(provider, handle, closure, file):
    """Idle callback to validate and apply emblems."""
    file_path = file.get_location().get_path()
    folder_path = os.path.dirname(file_path)

    log_debug_message(folder_path, f"Processing file in idle callback: {file_path}")

    if file_path in checksum_info and not has_emblem(file):
        if checksum_is_correct(file):
            # todo: The result of add_emblem() is recognised within Nautilus and emblem is displayed, but no "metadata::emblems" is listed using `gio info <file>`
            file.add_emblem(VERIFIED_EMBLEM)
            # todo: add_string_attribute() is not making any changes to the file. No emblem id displayed, no gio info is added.
            #file.add_string_attribute("metadata::emblems", VERIFIED_EMBLEM)
            log_debug_message(folder_path, f"Checksum verified and emblem applied for {file_path}")
        else:
            file.add_emblem(WRONG_EMBLEM)
            #file.add_string_attribute("metadata::emblems", WRONG_EMBLEM)
            log_debug_message(folder_path, f"Checksum mismatch and emblem applied for {file_path}")

    Nautilus.info_provider_update_complete_invoke(
        closure,
        provider,
        handle,
        Nautilus.OperationResult.COMPLETE,
    )
    return False  # Remove idle callback once done

class HashOverlayProvider(GObject.GObject, Nautilus.InfoProvider):
    def update_file_info_full(self, provider, handle, closure, file):
        """Update file info in Nautilus."""
        file_path = file.get_location().get_path()
        folder_path = os.path.dirname(file_path)

        #log_debug_message(folder_path, f"update_file_info_full called for: {file_path}")
        log_debug_message(folder_path, f"update_file_info_full called for: {file_path}")

        # Skip processing if the file is a directory
        #if file.get_uri_scheme() != "file":
        if os.path.isdir(file_path):
            log_debug_message(folder_path, f"Ignoring directory: {file_path}")
            Nautilus.info_provider_update_complete_invoke(
                closure,
                provider,
                handle,
                Nautilus.OperationResult.COMPLETE,
            )
            return
        elif not os.path.isfile(file_path):
            log_debug_message(folder_path, f"Ignoring, not a file either: {file_path}")
            Nautilus.info_provider_update_complete_invoke(
                closure,
                provider,
                handle,
                Nautilus.OperationResult.COMPLETE,
            )
            return

        log_debug_message(folder_path, f"Validating checksum for: {file_path}")

        if is_checksum(file):
            parse_add_checksum_info(file)
            log_debug_message(folder_path, f"Processed checksum file: {file_path}")
            return Nautilus.OperationResult.COMPLETE

        if not has_emblem(file):
            GObject.idle_add(update_cb, provider, handle, closure, file)
            log_debug_message(folder_path, f"Deferred file for checksum verification: {file_path}")
            return Nautilus.OperationResult.IN_PROGRESS

        log_debug_message(folder_path, f"No action needed for file: {file_path}")
        return Nautilus.OperationResult.COMPLETE
