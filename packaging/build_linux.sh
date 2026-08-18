#!/usr/bin/env bash
# Build the Linux distribution (single folder)
set -e
cd "$(dirname "$0")/.."
python3 -m PyInstaller --noconfirm --clean packaging/DrillingProgram.spec
echo "Done. Output: dist/DrillingProgram/"
