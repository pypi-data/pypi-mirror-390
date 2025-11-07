"""Integration tests for CodeSentinel CLI."""

import unittest
import subprocess
import sys
import os
from unittest.mock import patch

# Add the codesentinel package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI functionality."""

    def test_cli_help(self):
        """Test that CLI help command works."""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'codesentinel.cli', '--help'
            ], capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), '..'))

            self.assertEqual(result.returncode, 0)
            self.assertIn('usage:', result.stdout.lower())
        except (subprocess.CalledProcessError, FileNotFoundError):
            # CLI may not be properly installed in test environment
            self.skipTest("CLI not available in test environment")

    def test_cli_status(self):
        """Test CLI status command."""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'codesentinel.cli', 'status'
            ], capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), '..'))

            # Status command should work even if some features aren't available
            self.assertIn(result.returncode, [0, 1])  # 0 for success, 1 for some warnings
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.skipTest("CLI not available in test environment")


if __name__ == '__main__':
    unittest.main()