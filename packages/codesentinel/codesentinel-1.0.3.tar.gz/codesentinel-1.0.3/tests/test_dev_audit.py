"""Tests for DevAudit functionality."""

import unittest
import os
import sys
from pathlib import Path

# Ensure package import
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from codesentinel.core import CodeSentinel


class TestDevAudit(unittest.TestCase):
    def test_brief_audit_runs(self):
        cs = CodeSentinel()
        results = cs.run_dev_audit(interactive=False)
        self.assertIsInstance(results, dict)
        self.assertIn('summary', results)
        self.assertIn('security', results)


if __name__ == '__main__':
    unittest.main()
