# CodeSentinel Installation Guide

## Overview

CodeSentinel v1.0.0 provides multiple installation methods to suit different use cases, from quick pip installation to development setup from source.

## Requirements

- **Python:** 3.13+ (tested on 3.13 and 3.14)
- **Operating Systems:** Windows, Linux, macOS
- **Dependencies:** psutil (installed automatically)

## Installation Methods

### Method 1: Install from PyPI (Recommended)

For users who want to use CodeSentinel as a tool:

```bash
pip install codesentinel
```

Verify installation:

```bash
codesentinel status
```

### Method 2: Install from Source (Development)

For contributors or users who want the latest features:

```bash
# Clone the repository
git clone https://github.com/joediggidyyy/CodeSentinel.git
cd CodeSentinel

# Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Unix/Linux/macOS:
source .venv/bin/activate

# Install in editable mode
pip install -e .
```

### Method 3: Install from GitHub Release

For specific versions:

```bash
# Download wheel from GitHub releases
pip install https://github.com/joediggidyyy/CodeSentinel/releases/download/v1.0.0-beta.1/codesentinel-1.0.0-py3-none-any.whl
```

Or download and install locally:

```bash
# Download .whl file from https://github.com/joediggidyyy/CodeSentinel/releases
pip install codesentinel-1.0.0-py3-none-any.whl
```

## Configuration

### Quick Setup Wizard

Launch the GUI configuration wizard:

```bash
codesentinel-setup-gui
```

Or use platform-specific wrappers:

- **Windows:** Double-click `setup_wizard.bat`
- **Unix/Linux/macOS:** Run `./setup_wizard.sh`

The wizard guides you through:

1. Repository path selection
2. Alert configuration (email, Slack, GitHub)
3. Process monitoring setup
4. Security settings

### Manual Configuration

Create `codesentinel.json` in your project root:

```json
{
  "repository": {
    "path": "/path/to/your/project",
    "name": "ProjectName"
  },
  "alerts": {
    "email": {
      "enabled": false,
      "smtp_server": "",
      "smtp_port": 587,
      "from_address": "",
      "to_address": "",
      "password": ""
    },
    "slack": {
      "enabled": false,
      "webhook_url": ""
    },
    "github": {
      "enabled": false,
      "owner": "",
      "repo": "",
      "token": ""
    }
  },
  "process_monitor": {
    "enabled": false,
    "check_interval": 300
  }
}
```

## Post-Installation

### Verify Installation

```bash
# Check version and commands
codesentinel status

# View help
codesentinel --help
```

### Run First Audit

```bash
# Interactive development audit
codesentinel !!!!

# Or with agent-friendly output
codesentinel !!!! --agent
```

### Configure Your Project

```bash
# Launch GUI wizard for full configuration
codesentinel-setup-gui

# Or launch project setup
codesentinel-setup
```

## Command Reference

### Main CLI Commands

| Command | Description |
|---------|-------------|
| `codesentinel status` | Show system status and available commands |
| `codesentinel !!!!` | Run interactive development audit |
| `codesentinel !!!! --agent` | Run audit with agent-friendly output |
| `codesentinel-setup` | Launch project setup wizard |
| `codesentinel-setup-gui` | Launch GUI configuration wizard |

### Development Commands

```bash
# Run tests
python run_tests.py

# Or use pytest directly
pytest tests/

# Run with coverage
pytest --cov=codesentinel tests/
```

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: No module named 'codesentinel'`:

```bash
# Verify installation
pip list | grep codesentinel

# Reinstall if needed
pip install --force-reinstall codesentinel
```

### Permission Errors

On Unix/Linux/macOS, you may need to make scripts executable:

```bash
chmod +x setup_wizard.sh install.sh
```

### Virtual Environment Issues

Ensure your virtual environment is activated:

```bash
# Windows
.venv\Scripts\activate

# Unix/Linux/macOS
source .venv/bin/activate
```

### Python Version Issues

CodeSentinel requires Python 3.13+:

```bash
# Check your Python version
python --version

# Use specific Python version if needed
python3.13 -m pip install codesentinel
```

## Upgrading

### From PyPI

```bash
pip install --upgrade codesentinel
```

### From Source

```bash
cd CodeSentinel
git pull origin main
pip install -e . --upgrade
```

## Uninstallation

```bash
pip uninstall codesentinel
```

Configuration files in your project directories are not removed automatically.

## Next Steps

After installation:

1. **Read the [QUICKSTART.md](QUICKSTART.md)** for basic usage
2. **Configure alerts** using `codesentinel-setup-gui`
3. **Run your first audit** with `codesentinel !!!!`
4. **Set up process monitoring** in the GUI wizard
5. **Review the [README.md](README.md)** for full feature documentation

## Support

- **Issues:** <https://github.com/joediggidyyy/CodeSentinel/issues>
- **Security:** See [SECURITY.md](SECURITY.md)
- **Contributing:** See [CONTRIBUTING.md](CONTRIBUTING.md)

### Build Dependencies

- pip (auto-installed via ensurepip)
- setuptools (upgraded automatically)
- wheel (installed automatically)

## PATH Configuration

### Current Session

The installer automatically adds Python Scripts directory to the current session PATH, enabling immediate CLI usage.

### Permanent Configuration

Provides shell-specific instructions for:

- **Windows**: PowerShell profile, Command Prompt registry
- **Unix/Linux**: .bashrc, .zshrc, .profile
- **macOS**: .bash_profile, .zshrc

## Error Handling & Troubleshooting

### Common Issues Resolved

1. **Missing pip**: Auto-installed via ensurepip
2. **PATH not configured**: Automatic detection and setup
3. **Import errors**: Package structure fixes with **init**.py files
4. **Permission issues**: Provides --user installation guidance
5. **Platform differences**: Unified cross-platform handling

### Diagnostic Tools

- `check_dependencies.py --quiet` for CI/automation
- `check_dependencies.py --json` for programmatic integration
- Comprehensive error messages with specific remediation steps

## Testing & Validation

### Installation Testing

The installer validates:

- Package import capability
- CLI command availability
- Setup wizard functionality
- GUI wizard accessibility

### Continuous Integration

- Exit codes for automation (0 = success, 1 = failure)
- JSON output for parsing
- Quiet mode for minimal output

## Next Steps

After successful installation:

1. Run setup wizard: `codesentinel-setup` or `codesentinel-setup-gui`
2. Configure alerts: Edit `tools/config/alerts.json`
3. Set maintenance schedule: Edit `tools/config/scheduler.json`
4. Test functionality: `codesentinel status`

## Architecture Integration

This installation pipeline integrates with CodeSentinel's dual architecture:

- **Core package** (`codesentinel/`) gets proper CLI entry points
- **Tools scripts** (`tools/codesentinel/`) become accessible via PATH
- **Configuration files** (`tools/config/`) are created with defaults
- **Testing framework** works with both pytest and unittest

The installation system ensures that regardless of the user's Python environment state, CodeSentinel can be successfully installed and configured for immediate use.
