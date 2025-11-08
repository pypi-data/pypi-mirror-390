#!/bin/bash
# Build Talky Debian package

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================"
echo "Talky Debian Package Builder"
echo "================================"
echo

# Check if we're in the right directory
if [ ! -f "debian/control" ]; then
    echo -e "${RED}✗ Error: debian/control not found${NC}"
    echo "  Run this script from the project root directory"
    exit 1
fi

# Check for required tools
echo "Checking build dependencies..."
MISSING_DEPS=()

for cmd in dpkg-buildpackage debuild python3; do
    if ! command -v $cmd &> /dev/null; then
        MISSING_DEPS+=($cmd)
    fi
done

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo -e "${RED}✗ Missing build dependencies:${NC} ${MISSING_DEPS[*]}"
    echo
    echo "Install with:"
    echo "  sudo apt install debhelper dh-python python3-all python3-setuptools devscripts build-essential"
    exit 1
fi

echo -e "${GREEN}✓${NC} All build tools found"
echo

# Clean previous builds
echo "Cleaning previous builds..."
rm -f ../talky_*.deb ../talky_*.changes ../talky_*.buildinfo ../talky_*.tar.xz
rm -rf debian/talky debian/.debhelper debian/files debian/debhelper-build-stamp
echo -e "${GREEN}✓${NC} Cleaned"
echo

# Build package
echo "Building package..."
echo "This may take a few minutes..."
echo

if dpkg-buildpackage -us -uc -b; then
    echo
    echo "================================"
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo "================================"
    echo

    # Find the .deb file
    DEB_FILE=$(ls -t ../talky_*.deb 2>/dev/null | head -n1)

    if [ -n "$DEB_FILE" ]; then
        echo "Package created: $DEB_FILE"
        echo
        echo "Package info:"
        dpkg -I "$DEB_FILE" | grep -E "Package:|Version:|Architecture:|Description:"
        echo
        echo "Package size: $(du -h "$DEB_FILE" | cut -f1)"
        echo
        echo "To install:"
        echo "  sudo apt install $DEB_FILE"
        echo
        echo "Or:"
        echo "  sudo dpkg -i $DEB_FILE"
        echo "  sudo apt --fix-broken install  # if needed"
        echo
    fi

    # Run lintian if available
    if command -v lintian &> /dev/null && [ -n "$DEB_FILE" ]; then
        echo "Running lintian checks..."
        echo
        lintian "$DEB_FILE" || true
        echo
    fi

else
    echo
    echo "================================"
    echo -e "${RED}✗ Build failed!${NC}"
    echo "================================"
    echo
    echo "Check the error messages above."
    echo
    echo "Common issues:"
    echo "  - Missing build dependencies: sudo apt build-dep ./"
    echo "  - Syntax errors in debian/rules or debian/control"
    echo "  - Python packaging issues: check setup.py and pyproject.toml"
    echo
    exit 1
fi

exit 0
