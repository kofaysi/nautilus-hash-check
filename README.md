# Nautilus Hash Check

This script validates file hashes (MD5, SHA256, SHA1, SHA512) and adds emblems to files in Nautilus.

## Features
- Validates hashes using `.md5sum`, `.sha256sum`, `.sha1sum` and `.sha512sum` files.
- Applies `emblem-hash-verified` to verified files. The files are not validate repeatedly.
- Applies `emblem-hash-error` to verified files. The files may be validated repeatedly.

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

## Customization

The `assets/` folder contains the source file `green-check-icon.svg`, which was used to generate the `emblem-shield.png` file. You can modify the SVG and regenerate the PNG using a tool like Inkscape:

```bash
inkscape -w 48 -h 48 -o emblem-hash-verified.png --export-page=1 emblem-shield.svg  
inkscape -w 48 -h 48 -o emblem-hash-error.png --export-page=2 emblem-shield.svg
```
also

```bash
flatpak run org.inkscape.Inkscape -w 48 -h 48 -o emblem-hash-verified.png --export-page=1 emblem-shield.svg  
flatpak run org.inkscape.Inkscape -w 48 -h 48 -o emblem-hash-error.png --export-page=2 emblem-shield.svg
```

After modifying the icon, run the install.sh script again to update the installation.

## License
MIT
