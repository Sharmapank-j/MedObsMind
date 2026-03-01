# bin Directory

This directory contains utility scripts for the MedObsMind project.

## Scripts

### installdependencies.sh

Installs system dependencies required for running a GitHub Actions self-hosted runner.

**Purpose:** Resolves missing .NET Core 6.0 dependencies needed by the GitHub Actions runner.

**Usage:**
```bash
sudo ./bin/installdependencies.sh
```

**Supported Systems:**
- Ubuntu 20.04/22.04
- Debian
- RHEL
- CentOS
- Fedora

**What it installs:**
- .NET Core 6.0 runtime dependencies
- System libraries (libc6, libgcc, libstdc++, etc.)
- SSL/TLS libraries
- Kerberos libraries
- Additional required system packages

**Requirements:**
- Root or sudo access
- Internet connection for package downloads

**Documentation:** See [GITHUB_RUNNER_SETUP.md](../GITHUB_RUNNER_SETUP.md) for complete setup instructions.

---

## Adding New Scripts

When adding new scripts to this directory:

1. Make them executable: `chmod +x bin/yourscript.sh`
2. Add proper shebang: `#!/bin/bash`
3. Include usage documentation in comments
4. Add entry to this README
5. Test on target systems

---

**Last Updated:** February 9, 2026
