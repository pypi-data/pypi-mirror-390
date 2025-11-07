"""
CodeSentinel - Automated Maintenance & Security Monitoring
==========================================================

A Polymath Project | Created by joediggidyyy

SECURITY > EFFICIENCY > MINIMALISM

CodeSentinel provides automated maintenance, security monitoring, and alert systems
for development projects. It integrates seamlessly with GitHub, IDEs, and various
notification channels to keep your codebase healthy and secure.

Features:
- Automated maintenance scheduling and execution
- Security vulnerability scanning and alerts
- Multi-channel alert system (email, Slack, console, file)
- GitHub integration with Copilot support
- IDE integration (VS Code)
- Comprehensive setup wizards (CLI and GUI)

Author: joediggidyyy
License: MIT
"""

__version__ = "1.0.3"
__author__ = "joediggidyyy"
__license__ = "MIT"

from .core import CodeSentinel
from .cli import main

__all__ = ['CodeSentinel', 'main', '__version__', '__author__', '__license__']