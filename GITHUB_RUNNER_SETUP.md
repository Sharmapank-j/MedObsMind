# Self-Hosted GitHub Actions Runner Setup Guide

## Overview

This guide explains how to set up a self-hosted GitHub Actions runner for the MedObsMind project. Self-hosted runners allow you to run CI/CD workflows on your own infrastructure.

---

## Prerequisites

- A Linux server (Ubuntu 20.04/22.04, Debian, RHEL, CentOS, or Fedora)
- Root or sudo access
- At least 2GB RAM and 10GB disk space
- Network access to GitHub

---

## Problem: Missing .NET Core 6.0 Dependencies

When setting up a GitHub Actions runner, you may encounter errors like:

```
libgcc_s.so.1 => not found
libpthread.so.0 => not found
librt.so.1 => not found
libdl.so.2 => not found
libstdc++.so.6 => not found
libm.so.6 => not found
libc.so.6 => not found
ld-linux-x86-64.so.2 => not found
```

This occurs because the GitHub Actions runner requires .NET Core 6.0 runtime, which depends on these system libraries.

---

## Solution: Install Dependencies

We've provided a script to automatically install all required dependencies.

### Step 1: Download the GitHub Actions Runner

```bash
# Create a directory for the runner
mkdir -p ~/actions-runner && cd ~/actions-runner

# Download the latest runner package
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz

# Extract the installer
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz
```

### Step 2: Install Dependencies

Navigate to your MedObsMind repository and run the installation script:

```bash
# Navigate to the repository
cd /path/to/MedObsMind

# Run the dependency installation script with sudo
sudo ./bin/installdependencies.sh
```

The script will:
- Detect your operating system
- Install all required .NET Core 6.0 dependencies
- Install additional system libraries
- Verify the installation

### Step 3: Configure the Runner

```bash
# Navigate back to the runner directory
cd ~/actions-runner

# Create a personal access token (PAT) on GitHub:
# 1. Go to: https://github.com/settings/tokens
# 2. Click "Generate new token" (classic)
# 3. Select scopes: repo, workflow, admin:org (for org runners)
# 4. Copy the generated token

# Configure the runner
./config.sh --url https://github.com/Sharmapank-j/MedObsMind --token YOUR_TOKEN

# When prompted:
# - Runner name: Give it a descriptive name (e.g., "ubuntu-runner-1")
# - Runner group: Press Enter for default
# - Labels: Add custom labels if needed (e.g., "self-hosted,linux,x64")
# - Work folder: Press Enter for default (_work)
```

### Step 4: Run the Runner

#### Option A: Run Interactively (for testing)

```bash
./run.sh
```

Press `Ctrl+C` to stop the runner.

#### Option B: Run as a Service (recommended for production)

```bash
# Install the service
sudo ./svc.sh install

# Start the service
sudo ./svc.sh start

# Check status
sudo ./svc.sh status

# Enable auto-start on boot
sudo systemctl enable actions.runner.*
```

---

## Manual Dependency Installation

If you prefer to install dependencies manually:

### Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y \
  libc6 libgcc1 libgssapi-krb5-2 libicu-dev libssl-dev \
  libstdc++6 zlib1g libgcc-s1 ca-certificates curl wget \
  libkrb5-3 liblttng-ust0 libunwind8
```

### RHEL/CentOS/Fedora:

```bash
sudo yum install -y \
  ca-certificates krb5-libs libicu lttng-ust \
  openssl-libs zlib libgcc libstdc++
```

---

## Verification

After installation, verify that all dependencies are installed:

```bash
# Test .NET runtime
dotnet --info

# Check for missing libraries
ldd ~/actions-runner/bin/Runner.Listener
```

All libraries should show a path (not "not found").

---

## Troubleshooting

### Issue: Script fails with permission errors

**Solution:** Make sure to run the script with `sudo`:
```bash
sudo ./bin/installdependencies.sh
```

### Issue: Runner fails to start

**Solution:** Check the runner logs:
```bash
cat ~/actions-runner/_diag/Runner_*.log
```

### Issue: Dependencies still missing after installation

**Solution:** 
1. Verify your OS is supported (Ubuntu, Debian, RHEL, CentOS, Fedora)
2. Check if package repositories are accessible
3. Try manual installation from the section above

### Issue: Runner disconnects frequently

**Solution:**
1. Check network connectivity
2. Ensure firewall allows outbound HTTPS (port 443)
3. Check system resources (RAM, disk space)

---

## Managing the Runner

### Start the service:
```bash
sudo ./svc.sh start
```

### Stop the service:
```bash
sudo ./svc.sh stop
```

### Check status:
```bash
sudo ./svc.sh status
```

### View logs:
```bash
# Service logs
sudo journalctl -u actions.runner.* -f

# Runner diagnostic logs
tail -f ~/actions-runner/_diag/Runner_*.log
```

### Uninstall the service:
```bash
sudo ./svc.sh uninstall
```

---

## Security Considerations

1. **Isolation**: Run the runner as a dedicated user, not as root
2. **Network**: Ensure the runner can only access necessary resources
3. **Secrets**: Never commit runner tokens or sensitive data
4. **Updates**: Keep the runner software updated regularly
5. **Monitoring**: Monitor runner activity and logs for suspicious behavior

---

## Multiple Runners

To run multiple runners on the same machine:

```bash
# Create separate directories
mkdir -p ~/actions-runner-1 ~/actions-runner-2

# Configure each with different names
cd ~/actions-runner-1
./config.sh --url ... --name runner-1

cd ~/actions-runner-2
./config.sh --url ... --name runner-2

# Install and start services for each
sudo ./svc.sh install
sudo ./svc.sh start
```

---

## Updating the Runner

```bash
# Stop the runner
sudo ./svc.sh stop

# Navigate to runner directory
cd ~/actions-runner

# Download new version
curl -o actions-runner-linux-x64-NEW_VERSION.tar.gz -L \
  https://github.com/actions/runner/releases/download/vNEW_VERSION/actions-runner-linux-x64-NEW_VERSION.tar.gz

# Extract (this updates binaries)
tar xzf ./actions-runner-linux-x64-NEW_VERSION.tar.gz

# Start the runner
sudo ./svc.sh start
```

---

## Removing the Runner

```bash
# Stop and uninstall the service
sudo ./svc.sh stop
sudo ./svc.sh uninstall

# Navigate to runner directory
cd ~/actions-runner

# Remove the runner from GitHub
./config.sh remove --token YOUR_TOKEN

# Delete the runner directory
cd ~
rm -rf ~/actions-runner
```

---

## Using Self-Hosted Runners in Workflows

In your `.github/workflows/*.yml` files, specify the self-hosted runner:

```yaml
jobs:
  my-job:
    runs-on: self-hosted  # Use self-hosted runner
    # or
    runs-on: [self-hosted, linux, x64]  # Use with specific labels
    
    steps:
      - uses: actions/checkout@v3
      # ... rest of your workflow
```

---

## Resources

- [GitHub Actions Self-Hosted Runner Documentation](https://docs.github.com/en/actions/hosting-your-own-runners)
- [Runner Releases](https://github.com/actions/runner/releases)
- [.NET Core Dependencies](https://docs.microsoft.com/en-us/dotnet/core/install/linux)

---

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review runner logs in `~/actions-runner/_diag/`
3. Open an issue on the repository
4. Contact the development team

---

**Last Updated:** February 9, 2026  
**Script Version:** 1.0
