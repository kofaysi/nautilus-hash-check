# Nautilus Hash Check

This script validates file hashes (MD5, SHA256) and adds emblems to files in Nautilus.

## Features
- Validates hashes using `.md5sum` and `.sha256sum` files.
- Applies `emblem-shield` to verified files.

## Requirements

### Python Dependencies
- `pycairo`
- `PyGObject`

Install these dependencies using:
```bash
pip3 install -r requirements.txt
```

### System Dependencies
- `python3-nautilus`

Install this package using your system package manager. For example, on Ubuntu/Debian:
```bash
sudo apt install python3-nautilus
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/nautilus-hash-check.git
   cd nautilus-hash-check
   ```

2. Run the installation script:
   ```bash
   ./install.sh
   ```

3. Restart Nautilus:
   ```bash
   nautilus -q && nautilus &
   ```

## Usage

Place hash files in the same folder as the target files. Nautilus will automatically validate the hashes and apply emblems to verified files.

## Uninstallation

To remove the extension, run:
```bash
./uninstall.sh
```

## License
MIT
