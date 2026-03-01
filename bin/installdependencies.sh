#!/bin/bash
#
# Install dependencies for .NET Core 6.0 runtime
# Required for GitHub Actions self-hosted runner
#
# Usage: sudo ./bin/installdependencies.sh
#

set -e

echo "==========================================="
echo "Installing .NET Core 6.0 Dependencies"
echo "==========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Error: This script must be run as root or with sudo"
    echo "Usage: sudo ./bin/installdependencies.sh"
    exit 1
fi

# Detect OS and distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo "Error: Cannot detect OS distribution"
    exit 1
fi

echo "Detected OS: $OS $VER"
echo ""

# Function to install dependencies on Ubuntu/Debian
install_ubuntu_debian() {
    echo "Installing dependencies for Ubuntu/Debian..."
    
    # Update package lists
    echo "Updating package lists..."
    apt-get update
    
    # Install .NET Core runtime dependencies
    echo "Installing .NET Core runtime dependencies..."
    apt-get install -y \
        libc6 \
        libgcc1 \
        libgssapi-krb5-2 \
        libicu-dev \
        libssl-dev \
        libstdc++6 \
        zlib1g \
        libgcc-s1 \
        ca-certificates \
        curl \
        wget
    
    # Install additional required libraries
    echo "Installing additional system libraries..."
    apt-get install -y \
        libkrb5-3 \
        liblttng-ust0 \
        libunwind8
    
    echo "✅ Dependencies installed successfully!"
}

# Function to install dependencies on RHEL/CentOS/Fedora
install_rhel_centos() {
    echo "Installing dependencies for RHEL/CentOS/Fedora..."
    
    # Install .NET Core runtime dependencies
    echo "Installing .NET Core runtime dependencies..."
    yum install -y \
        ca-certificates \
        krb5-libs \
        libicu \
        lttng-ust \
        openssl-libs \
        zlib \
        libgcc \
        libstdc++
    
    echo "✅ Dependencies installed successfully!"
}

# Install based on detected OS
case "$OS" in
    ubuntu|debian)
        install_ubuntu_debian
        ;;
    rhel|centos|fedora)
        install_rhel_centos
        ;;
    *)
        echo "Error: Unsupported OS: $OS"
        echo "This script supports: Ubuntu, Debian, RHEL, CentOS, Fedora"
        exit 1
        ;;
esac

echo ""
echo "==========================================="
echo "Installation Complete!"
echo "==========================================="
echo ""
echo "You can now configure the GitHub Actions runner."
echo "Run: ./config.sh --url https://github.com/YOUR_ORG/YOUR_REPO --token YOUR_TOKEN"
echo ""
