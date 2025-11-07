"""Tests for CodeSentinel configuration utilities."""

import unittest
import tempfile
import json
import os
import sys

# Add the codesentinel package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from codesentinel.utils.config import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test cases for the ConfigManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'test_config.json')
        self.cm = ConfigManager(config_file=self.config_file)

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)

    def test_initialization(self):
        """Test that ConfigManager initializes correctly."""
        self.assertIsInstance(self.cm, ConfigManager)
        self.assertEqual(self.cm.config_file, self.config_file)

    def test_load_config_nonexistent(self):
        """Test loading config when file doesn't exist."""
        config = self.cm.load_config()
        self.assertIsInstance(config, dict)
        self.assertEqual(config, {})

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        test_config = {
            'alerts': {'email': 'test@example.com'},
            'maintenance': {'schedule': 'daily'}
        }

        self.cm.save_config(test_config)
        loaded_config = self.cm.load_config()

        self.assertEqual(loaded_config, test_config)

    def test_validate_config_valid(self):
        """Test config validation with valid config."""
        valid_config = {
            'alerts': {
                'email': {'enabled': True, 'smtp_server': 'smtp.example.com'},
                'slack': {'enabled': False}
            },
            'maintenance': {
                'schedule': 'daily'
            }
        }

        is_valid, errors = self.cm.validate_config(valid_config)
        self.assertTrue(is_valid)
        self.assertEqual(errors, [])

    def test_validate_config_invalid(self):
        """Test config validation with invalid config."""
        invalid_config = {
            'alerts': {
                'email': {'enabled': True}  # Missing required smtp_server
            }
        }

        is_valid, errors = self.cm.validate_config(invalid_config)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


if __name__ == '__main__':
    unittest.main()