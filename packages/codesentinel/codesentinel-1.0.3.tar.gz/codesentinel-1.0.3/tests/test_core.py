"""Tests for CodeSentinel core functionality."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the codesentinel package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from codesentinel import __version__
from codesentinel.core import CodeSentinel


class TestCodeSentinel(unittest.TestCase):
    """Test cases for the CodeSentinel core class."""

    def setUp(self):
        """Set up test fixtures."""
        self.cs = CodeSentinel()

    def test_initialization(self):
        """Test that CodeSentinel initializes correctly."""
        self.assertIsInstance(self.cs, CodeSentinel)
        self.assertEqual(self.cs.version, __version__)

    @patch('codesentinel.core.subprocess.run')
    def test_run_security_scan(self, mock_subprocess):
        """Test security scan execution."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="Security scan completed")

        result = self.cs.run_security_scan()

        self.assertTrue(result)
        mock_subprocess.assert_called_once()

    @patch('codesentinel.core.subprocess.run')
    def test_run_maintenance_tasks(self, mock_subprocess):
        """Test maintenance tasks execution."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="Maintenance completed")

        result = self.cs.run_maintenance_tasks()

        self.assertTrue(result)
        mock_subprocess.assert_called_once()

    def test_get_status(self):
        """Test status reporting."""
        status = self.cs.get_status()

        self.assertIsInstance(status, dict)
        self.assertIn('version', status)
        self.assertIn('status', status)
        self.assertEqual(status['version'], __version__)


if __name__ == '__main__':
    unittest.main()