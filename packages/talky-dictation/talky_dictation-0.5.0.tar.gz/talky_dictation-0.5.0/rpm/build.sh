#!/bin/bash
# RPM package build script for Talky
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VERSION=$(grep "^VERSION = " "$PROJECT_ROOT/src/talky/version.py" | cut -d'"' -f2)

echo "========================================"
echo "Talky RPM Package Builder"
echo "========================================"
echo "Version: $VERSION"
echo ""

# Check if rpmbuild is installed
if ! command -v rpmbuild &> /dev/null; then
    echo "Error: rpmbuild not found!"
    echo ""
    echo "Install with:"
    echo "  Fedora/RHEL: sudo dnf install rpm-build rpmdevtools"
    echo "  openSUSE: sudo zypper install rpm-build"
    exit 1
fi

# Check if python3-devel is installed
if ! rpm -q python3-devel &> /dev/null; then
    echo "Warning: python3-devel not found!"
    echo "Install with: sudo dnf install python3-devel"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Setup rpmbuild directory structure
echo "Setting up rpmbuild directories..."
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Create source tarball
echo "Creating source tarball..."
TARBALL="talky-${VERSION}.tar.gz"
cd "$PROJECT_ROOT/.."
tar czf "$TARBALL" \
    --exclude='talky/.git' \
    --exclude='talky/.env' \
    --exclude='talky/__pycache__' \
    --exclude='talky/**/__pycache__' \
    --exclude='talky/venv' \
    --exclude='talky/.venv' \
    --exclude='talky/dist' \
    --exclude='talky/build' \
    --exclude='talky/*.egg-info' \
    --exclude='talky/.pytest_cache' \
    --exclude='talky/.mypy_cache' \
    talky/

# Move tarball to SOURCES
mv "$TARBALL" ~/rpmbuild/SOURCES/
echo "Source tarball created: ~/rpmbuild/SOURCES/$TARBALL"

# Copy spec file
cp "$SCRIPT_DIR/talky.spec" ~/rpmbuild/SPECS/
echo "Spec file copied: ~/rpmbuild/SPECS/talky.spec"

# Build the RPM
echo ""
echo "Building RPM package..."
echo "========================================"
cd ~/rpmbuild/SPECS
rpmbuild -ba talky.spec

# Check if build succeeded
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "Build successful!"
    echo "========================================"
    echo ""
    echo "Binary RPM: ~/rpmbuild/RPMS/noarch/talky-${VERSION}-1.*.noarch.rpm"
    echo "Source RPM: ~/rpmbuild/SRPMS/talky-${VERSION}-1.*.src.rpm"
    echo ""
    echo "To install:"
    echo "  sudo dnf install ~/rpmbuild/RPMS/noarch/talky-${VERSION}-1.*.noarch.rpm"
    echo ""
    echo "To test installation:"
    echo "  rpm -qlp ~/rpmbuild/RPMS/noarch/talky-${VERSION}-1.*.noarch.rpm"
    echo ""
    echo "To run quality checks:"
    echo "  rpmlint ~/rpmbuild/RPMS/noarch/talky-${VERSION}-1.*.noarch.rpm"
    echo "  rpmlint ~/rpmbuild/SPECS/talky.spec"
else
    echo ""
    echo "========================================"
    echo "Build failed!"
    echo "========================================"
    echo "Check the output above for errors."
    exit 1
fi
