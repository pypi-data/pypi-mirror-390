#!/usr/bin/env python3
"""
CodeSentinel Package Launcher

Entry point wrapper for the main launcher script.
"""

import sys
import os
from pathlib import Path

def main():
    """Package entry point that delegates to the main launcher."""
    # Add the project root to the Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Import and run the main launcher
    try:
        from launch import main as launcher_main
        return launcher_main()
    except Exception as e:
        print(f"❌ Failed to launch CodeSentinel setup: {e}")
        print("   Please run directly: python launch.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())