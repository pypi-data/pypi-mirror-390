"""
Tests for process monitor functionality.
"""

import unittest
import time
import subprocess
import sys
from pathlib import Path

try:
    from codesentinel.utils.process_monitor import ProcessMonitor, get_monitor
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@unittest.skipUnless(PSUTIL_AVAILABLE, "psutil not available")
class TestProcessMonitor(unittest.TestCase):
    """Test cases for ProcessMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monitor = ProcessMonitor(check_interval=1, enabled=True)
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'monitor'):
            self.monitor.stop()
    
    def test_monitor_initialization(self):
        """Test that monitor initializes correctly."""
        self.assertIsNotNone(self.monitor)
        self.assertEqual(self.monitor.check_interval, 1)
        self.assertTrue(self.monitor.enabled)
        self.assertEqual(len(self.monitor.tracked_pids), 0)
    
    def test_track_untrack_process(self):
        """Test tracking and untracking processes."""
        test_pid = 12345
        
        # Track a PID
        self.monitor.track_process(test_pid)
        self.assertIn(test_pid, self.monitor.tracked_pids)
        
        # Untrack the PID
        self.monitor.untrack_process(test_pid)
        self.assertNotIn(test_pid, self.monitor.tracked_pids)
    
    def test_start_stop_monitor(self):
        """Test starting and stopping the monitor."""
        # Start monitor
        self.monitor.start()
        time.sleep(0.5)  # Give it time to start
        
        status = self.monitor.get_status()
        self.assertTrue(status['running'])
        self.assertTrue(status['enabled'])
        
        # Stop monitor
        self.monitor.stop()
        time.sleep(0.5)  # Give it time to stop
        
        status = self.monitor.get_status()
        self.assertFalse(status['running'])
    
    def test_get_status(self):
        """Test getting monitor status."""
        status = self.monitor.get_status()
        
        self.assertIn('enabled', status)
        self.assertIn('running', status)
        self.assertIn('parent_pid', status)
        self.assertIn('tracked_pids', status)
        self.assertIn('tracked_count', status)
        self.assertIn('check_interval', status)
        
        self.assertTrue(status['enabled'])
        self.assertEqual(status['check_interval'], 1)
    
    def test_monitor_with_real_process(self):
        """Test monitor with a real subprocess."""
        # Create a simple subprocess
        if sys.platform == 'win32':
            proc = subprocess.Popen(['ping', 'localhost', '-n', '5'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
        else:
            proc = subprocess.Popen(['sleep', '5'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
        
        try:
            # Track the process
            self.monitor.track_process(proc.pid)
            self.assertIn(proc.pid, self.monitor.tracked_pids)
            
            # Start monitor
            self.monitor.start()
            time.sleep(0.5)
            
            # Process should still be tracked (it's running)
            self.assertIn(proc.pid, self.monitor.tracked_pids)
            
            # Terminate the process
            proc.terminate()
            proc.wait(timeout=5)
            
            # Give monitor time to detect termination
            time.sleep(2)
            
            # Process should be untracked now
            self.assertNotIn(proc.pid, self.monitor.tracked_pids)
            
        finally:
            # Ensure cleanup
            try:
                proc.kill()
            except:
                pass
            self.monitor.stop()
    
    def test_global_monitor(self):
        """Test global monitor singleton."""
        monitor1 = get_monitor()
        monitor2 = get_monitor()
        
        # Should be the same instance
        self.assertIs(monitor1, monitor2)


if __name__ == '__main__':
    unittest.main()
