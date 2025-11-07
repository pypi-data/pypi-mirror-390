# CodeSentinel - Quick Start

## Security-First Automated Maintenance and Monitoring

## Installation

### From PyPI (Recommended)

```bash
pip install codesentinel
```

### From Source

```bash
git clone https://github.com/joediggidyyy/CodeSentinel.git
cd CodeSentinel
pip install -e .
```

## Getting Started

### CLI Commands

```bash
# Show status and available commands
codesentinel status

# Run development audit (interactive)
codesentinel !!!!

# Run development audit (agent-friendly output)
codesentinel !!!! --agent

# Launch GUI setup wizard
codesentinel-setup-gui

# Launch project setup
codesentinel-setup
```

### Quick Setup Wizards

**Windows:** Double-click `setup_wizard.bat`  
**Unix/Linux/macOS:** Run `./setup_wizard.sh`

These wrappers launch the GUI configuration wizard for:

- Repository configuration
- Alert system setup (email, Slack, GitHub)
- Process monitoring configuration
- Security settings

## Architecture

**SECURITY > EFFICIENCY > MINIMALISM**

---

*For detailed documentation, see the full README.md*
