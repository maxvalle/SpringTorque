#!/bin/bash
set -e

# Detect OS
OS="$(uname -s)"
case "$OS" in
  Darwin) PLATFORM="macos" ;;
  Linux)  PLATFORM="linux" ;;
  *)
    echo "Unsupported OS: $OS"
    exit 1
    ;;
esac

echo "Building for $PLATFORM..."

# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Build
if [ "$PLATFORM" = "macos" ]; then
  python -m nuitka \
    --standalone \
    --macos-create-app-bundle \
    --enable-plugin=pyside6 \
    --follow-imports \
    --include-package=PySide6 \
    --macos-app-name=SpringTorque \
    --output-dir=dist \
    springtorque.py

  # 4. Sign with entitlements (ad-hoc)
  codesign --deep --force --sign - \
    --entitlements macOS/entitlements.plist \
    dist/SpringTorque.app

else
  python -m nuitka \
    --onefile \
    --enable-plugin=pyside6 \
    --follow-imports \
    --include-package=PySide6 \
    --output-filename=SpringTorque \
    --output-dir=dist \
    springtorque.py
fi

# 5. Deactivate virtual environment
deactivate

# 6. Clean up
rm -rf venv
rm -rf __pycache__

# 7. Done
if [ "$PLATFORM" = "macos" ]; then
  echo "Done! Check dist/SpringTorque.app"
else
  echo "Done! Check dist/SpringTorque"
fi