import os
import hashlib
import threading
import subprocess
import time
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

# Define a unique debug file path based on the script name
SCRIPT_NAME = os.path.basename(__file__).replace('.py', '')
DEBUG_FILE = f"/tmp/{SCRIPT_NAME}_debug.log"

VALIDATION_IN_PROGRESS = set()  # Set of files currently being validated
VALIDATION_CACHE = {}  # Cache: {file_path: last_validation_timestamp}
CACHE_EXPIRY_SECONDS = 10  # Time to skip re-validation for the same file
VALIDATION_LOCK = threading.Lock()  # Thread lock for validation tracking

# Name of the emblem to apply
VERIFIED_EMBLEM = "emblem-hash-verified"
FAILED_EMBLEM = "emblem-hash-error"

# Global flag to control debug logging
ENABLE_DEBUG_LOGGING = True  # Set to False to disable logging

def log_debug_message(folder_path, message):
    """Log debug messages to a global debug file with timestamps if logging is enabled."""
    if not ENABLE_DEBUG_LOGGING:
        return  # Skip logging if disabled

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

def is_recently_validated(file_path):
    """Check if the file was recently validated."""
    now = time.time()
    last_validated = VALIDATION_CACHE.get(file_path, 0)
    return (now - last_validated) < CACHE_EXPIRY_SECONDS

def read_hash_file(hash_file_path):
    """Read and parse the hash file into lines."""
    try:
        with open(hash_file_path, "r") as f:
            return [line.strip() for line in f.readlines()]
    except Exception as e:
        log_debug_message(os.path.dirname(hash_file_path), f"Error reading {hash_file_path}: {e}")
        return []

def parse_hash_line(line):
    """Parse a single line into hash value and file name."""
    try:
        hash_value, file_name = line.split("  ", 1)
        return hash_value, file_name
    except ValueError:
        log_debug_message("", f"Malformed line: {line}")
        return None, None

def validate_hash(file_path, hash_value, hash_function):
    """Validate a file's hash against the expected value."""
    try:
        calculated_hash = calculate_file_hash(file_path, hash_function)
        return calculated_hash == hash_value
    except Exception as e:
        log_debug_message(os.path.dirname(file_path), f"Error validating hash for {file_path}: {e}")
        return False

def process_validation(file_path, hash_value, hash_function, working_folder):
    """Process the validation and apply the appropriate emblem."""
    if validate_hash(file_path, hash_value, hash_function):
        log_debug_message(working_folder, f"Hash validated for {file_path}")
        apply_emblem(file_path, VERIFIED_EMBLEM)
        return True
    else:
        log_debug_message(working_folder, f"Hash mismatch for {file_path}")

        # Skip files that already have an FAILED_EMBLEM applied
        if is_emblem_applied(file_path, FAILED_EMBLEM):
            log_debug_message(working_folder, f"Skipping {file_path} (emblem already applied)")
        else:
            apply_emblem(file_path, FAILED_EMBLEM)
        return False

def validate_file(file_path, hash_file_path, working_folder):
    """Validate the file's hash against the hash file."""
    lines = read_hash_file(hash_file_path)
    for line in lines:
        hash_value, file_name = parse_hash_line(line)
        if not hash_value or not file_name:
            continue

        if os.path.basename(file_path) == file_name:
            hash_function = get_hash_function(os.path.splitext(hash_file_path)[1])
            if not hash_function:
                log_debug_message(working_folder, f"Unsupported hash type in {hash_file_path}")
                return False

            return process_validation(file_path, hash_value, hash_function, working_folder)

    log_debug_message(working_folder, f"No matching hash entry found for {file_path}")
    return False

def should_validate_file(file_path):
    """Check if the file should be validated (not in progress and not recently validated)."""
    with VALIDATION_LOCK:
        if file_path in VALIDATION_IN_PROGRESS or is_recently_validated(file_path):
            return False
    return True

def add_to_in_progress(file_path):
    """Mark a file as being validated."""
    with VALIDATION_LOCK:
        VALIDATION_IN_PROGRESS.add(file_path)

def remove_from_in_progress(file_path):
    """Remove a file from the in-progress validation set."""
    with VALIDATION_LOCK:
        VALIDATION_IN_PROGRESS.discard(file_path)

def update_validation_cache(file_path):
    """Update the validation cache for a file."""
    with VALIDATION_LOCK:
        VALIDATION_CACHE[file_path] = time.time()

def validate_file_with_tracking(file_path, hash_file_path, working_folder):
    """Validate the file with tracking to avoid redundant validations."""
    if not should_validate_file(file_path):
        log_debug_message(working_folder, f"Skipping {file_path} (recently validated or in progress)")
        return False

    add_to_in_progress(file_path)

    try:
        # Perform validation
        if validate_file(file_path, hash_file_path, working_folder):
            update_validation_cache(file_path)
            return True
    finally:
        remove_from_in_progress(file_path)

    return False

def apply_emblem(file_path, emblem_name):
    """Apply an emblem to the file."""
    try:
        log_debug_message(os.path.dirname(file_path), f"Applying emblem '{emblem_name}' to {file_path}")
        subprocess.run(
            ["gio", "set", "-t", "stringv", file_path, "metadata::emblems", emblem_name],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        log_debug_message(os.path.dirname(file_path), f"Error applying emblem to {file_path}: {e}")

def is_supported_hash_file(file_path):
    """Check if the file has a supported hash file extension."""
    return any(file_path.endswith(ext) for ext in HASH_FILE_EXTENSIONS)


def process_hash_file(hash_file_path, folder_path):
    """Process a hash file and validate each target file."""
    lines = read_hash_file(hash_file_path)

    for line in lines:
        hash_value, file_name = parse_hash_line(line)
        if not hash_value or not file_name:
            continue

        file_path = os.path.join(folder_path, file_name)

        if not os.path.exists(file_path):
            log_debug_message(folder_path, f"Target file not found: {file_name}")
            continue

        # Skip files that already have an VERIFIED_EMBLEM applied
        if is_emblem_applied(file_path, VERIFIED_EMBLEM):
            log_debug_message(folder_path, f"Skipping {file_path} (emblem already applied)")
            continue

        # Validate the target file
        validate_file_with_tracking(file_path, hash_file_path, folder_path)


class HashOverlayProvider(GObject.GObject, Nautilus.InfoProvider):
    def update_file_info(self, file):
        """Update file info in Nautilus."""
        if file.get_uri_scheme() != "file":
            return

        file_path = file.get_location().get_path()

        # Ignore non-hash files
        if not is_supported_hash_file(file_path):
            return

        folder_path = os.path.dirname(file_path)

        # Run hash validation in a separate thread
        self._start_validation_thread(file_path, folder_path)

    def _start_validation_thread(self, file_path, folder_path):
        """Start a thread for validating a hash file."""
        def validate_and_process():
            log_debug_message(folder_path, f"Processing hash file: {file_path}")
            process_hash_file(file_path, folder_path)

        threading.Thread(target=validate_and_process, daemon=True).start()

