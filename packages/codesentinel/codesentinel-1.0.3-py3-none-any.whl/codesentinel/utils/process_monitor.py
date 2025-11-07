"""
Low-cost daemon for monitoring and cleaning up orphan processes.

⚠️ PERMANENT CORE FUNCTION - DO NOT REMOVE ⚠️
This module is a permanent feature of CodeSentinel and must persist through all versions.
It provides critical functionality for preventing resource leaks and managing orphaned processes.

This module provides a lightweight background monitor that:
- Tracks CodeSentinel-spawned processes
- Detects orphaned child processes
- Cleans up zombie/defunct processes
- Minimal CPU/memory footprint

SECURITY > EFFICIENCY > MINIMALISM
- Security: Prevents orphaned processes from consuming resources
- Efficiency: Low-cost background monitoring (default: 60 second intervals)
- Minimalism: Focused single-purpose daemon with minimal dependencies
"""

import os
import sys
import time
import psutil
import threading
import logging
from pathlib import Path
from typing import Set, Optional
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class ProcessMonitor:
    """
    Lightweight daemon to monitor and clean up orphan processes.
    
    Features:
    - Tracks child processes spawned by CodeSentinel
    - Detects orphaned processes (parent terminated but child still running)
    - Cleans up zombie/defunct processes
    - Minimal resource usage (sleeps between checks)
    """
    
    def __init__(self, check_interval: int = 60, enabled: bool = True):
        """
        Initialize the process monitor.
        
        Args:
            check_interval: Seconds between orphan checks (default: 60)
            enabled: Whether monitoring is active (default: True)
        """
        self.check_interval = check_interval
        self.enabled = enabled
        self.tracked_pids: Set[int] = set()
        self.parent_pid = os.getpid()
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        
        logger.debug(f"ProcessMonitor initialized (parent PID: {self.parent_pid})")
    
    def track_process(self, pid: int) -> None:
        """
        Add a process ID to tracking list.
        
        Args:
            pid: Process ID to track
        """
        with self._lock:
            self.tracked_pids.add(pid)
            logger.debug(f"Now tracking PID {pid}")
    
    def untrack_process(self, pid: int) -> None:
        """
        Remove a process ID from tracking list.
        
        Args:
            pid: Process ID to stop tracking
        """
        with self._lock:
            self.tracked_pids.discard(pid)
            logger.debug(f"Stopped tracking PID {pid}")
    
    def start(self) -> None:
        """Start the background monitoring daemon."""
        if not self.enabled:
            logger.debug("ProcessMonitor disabled, not starting")
            return
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            logger.warning("ProcessMonitor already running")
            return
        
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="ProcessMonitor",
            daemon=True
        )
        self._monitor_thread.start()
        logger.info("ProcessMonitor daemon started")
    
    def stop(self) -> None:
        """Stop the background monitoring daemon."""
        if not self._monitor_thread or not self._monitor_thread.is_alive():
            logger.debug("ProcessMonitor not running")
            return
        
        logger.info("Stopping ProcessMonitor daemon...")
        self._stop_event.set()
        self._monitor_thread.join(timeout=5)
        logger.info("ProcessMonitor daemon stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop (runs in background thread)."""
        logger.debug("ProcessMonitor loop started")
        
        while not self._stop_event.is_set():
            try:
                self._check_orphans()
                self._cleanup_zombies()
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}", exc_info=True)
            
            # Sleep with interrupt check
            self._stop_event.wait(timeout=self.check_interval)
        
        logger.debug("ProcessMonitor loop exited")
    
    def _check_orphans(self) -> None:
        """Check for orphaned processes and clean them up."""
        with self._lock:
            pids_to_check = list(self.tracked_pids)
        
        if not pids_to_check:
            return
        
        orphans_found = []
        
        for pid in pids_to_check:
            try:
                proc = psutil.Process(pid)
                
                # Check if process still exists
                if not proc.is_running():
                    self.untrack_process(pid)
                    continue
                
                # Check if parent is still our process
                try:
                    parent = proc.parent()
                    if parent is None or parent.pid != self.parent_pid:
                        # Orphaned: parent changed or doesn't exist
                        orphans_found.append(pid)
                        logger.warning(f"Orphaned process detected: PID {pid} ({proc.name()})")
                        
                        # Attempt graceful termination
                        try:
                            proc.terminate()
                            # Give it 5 seconds to terminate gracefully
                            proc.wait(timeout=5)
                            logger.info(f"Terminated orphaned process: PID {pid}")
                        except psutil.TimeoutExpired:
                            # Force kill if it doesn't terminate
                            proc.kill()
                            logger.warning(f"Force killed orphaned process: PID {pid}")
                        except psutil.AccessDenied:
                            logger.error(f"Access denied terminating PID {pid}")
                        
                        self.untrack_process(pid)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process no longer exists or we can't access it
                    self.untrack_process(pid)
            
            except psutil.NoSuchProcess:
                # Process already terminated
                self.untrack_process(pid)
            except Exception as e:
                logger.error(f"Error checking PID {pid}: {e}")
        
        if orphans_found:
            logger.info(f"Cleaned up {len(orphans_found)} orphaned process(es)")
    
    def _cleanup_zombies(self) -> None:
        """Clean up any zombie/defunct child processes."""
        try:
            current_proc = psutil.Process(self.parent_pid)
            children = current_proc.children(recursive=False)
            
            for child in children:
                try:
                    # Check if zombie/defunct
                    if child.status() == psutil.STATUS_ZOMBIE:
                        logger.warning(f"Zombie process detected: PID {child.pid}")
                        # Wait on the zombie to clean it up
                        try:
                            os.waitpid(child.pid, os.WNOHANG)
                            logger.info(f"Cleaned up zombie process: PID {child.pid}")
                        except (OSError, ChildProcessError):
                            pass  # Already cleaned or not our child
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        except Exception as e:
            logger.error(f"Error cleaning zombies: {e}")
    
    def get_status(self) -> dict:
        """
        Get current monitor status.
        
        Returns:
            dict: Status information including tracked PIDs and state
        """
        with self._lock:
            tracked = list(self.tracked_pids)
        
        return {
            'enabled': self.enabled,
            'running': self._monitor_thread and self._monitor_thread.is_alive(),
            'parent_pid': self.parent_pid,
            'tracked_pids': tracked,
            'tracked_count': len(tracked),
            'check_interval': self.check_interval,
        }


# Global singleton instance
_global_monitor: Optional[ProcessMonitor] = None


def get_monitor(check_interval: int = 60, enabled: bool = True) -> ProcessMonitor:
    """
    Get or create the global ProcessMonitor instance.
    
    Args:
        check_interval: Seconds between checks (only used on first call)
        enabled: Whether monitoring is enabled (only used on first call)
    
    Returns:
        ProcessMonitor: The global monitor instance
    """
    global _global_monitor
    
    if _global_monitor is None:
        _global_monitor = ProcessMonitor(
            check_interval=check_interval,
            enabled=enabled
        )
    
    return _global_monitor


def start_monitor(check_interval: int = 60, enabled: bool = True) -> ProcessMonitor:
    """
    Start the global process monitor daemon.
    
    Args:
        check_interval: Seconds between orphan checks
        enabled: Whether monitoring is active
    
    Returns:
        ProcessMonitor: The started monitor instance
    """
    monitor = get_monitor(check_interval=check_interval, enabled=enabled)
    
    # Prevent "already running" warning - if already running, skip gracefully
    if monitor._monitor_thread and monitor._monitor_thread.is_alive():
        logger.debug("ProcessMonitor already running, skipping start")
    else:
        monitor.start()
    
    return monitor


def stop_monitor() -> None:
    """Stop the global process monitor daemon."""
    global _global_monitor
    
    if _global_monitor is not None:
        _global_monitor.stop()
        # Reset global instance so next start() creates fresh monitor
        # This prevents "already running" warnings on repeated CLI invocations
        _global_monitor = None
        logger.debug("ProcessMonitor instance reset for next invocation")


def track_process(pid: int) -> None:
    """
    Track a process ID for orphan detection.
    
    Args:
        pid: Process ID to track
    """
    monitor = get_monitor()
    monitor.track_process(pid)


def untrack_process(pid: int) -> None:
    """
    Stop tracking a process ID.
    
    Args:
        pid: Process ID to stop tracking
    """
    if _global_monitor is not None:
        _global_monitor.untrack_process(pid)
