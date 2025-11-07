# Process Monitor

## Overview

CodeSentinel includes a low-cost daemon that monitors and cleans up orphan processes. This ensures that child processes spawned by CodeSentinel operations don't become orphaned or turn into zombies.

## Features

- **Orphan Detection**: Identifies processes whose parent has terminated
- **Zombie Cleanup**: Automatically reaps zombie/defunct processes
- **Low Resource Usage**: Checks occur every 60 seconds (configurable)
- **Thread-Safe**: Safe to use in multi-threaded applications
- **Automatic Startup**: Starts automatically when using CodeSentinel CLI

## Usage

### Automatic (Recommended)

The process monitor starts automatically when you use any CodeSentinel CLI command:

```bash
codesentinel status      # Monitor starts automatically
codesentinel scan        # Monitor is running in background
codesentinel !!!!        # Monitor active during audit
```

### Manual Control

```python
from codesentinel.utils.process_monitor import start_monitor, stop_monitor, track_process

# Start the monitor (checks every 60 seconds)
monitor = start_monitor(check_interval=60, enabled=True)

# Track a subprocess
import subprocess
proc = subprocess.Popen(['python', 'script.py'])
track_process(proc.pid)

# The monitor will automatically clean up if the process becomes orphaned

# Stop the monitor when done
stop_monitor()
```

### Tracking Processes

To track a process for orphan detection:

```python
from codesentinel.utils.process_monitor import track_process, untrack_process

# Track a process
track_process(12345)

# Later, when process is no longer needed
untrack_process(12345)
```

### Getting Status

```python
from codesentinel.utils.process_monitor import get_monitor

monitor = get_monitor()
status = monitor.get_status()

print(f"Monitor enabled: {status['enabled']}")
print(f"Monitor running: {status['running']}")
print(f"Tracked processes: {status['tracked_count']}")
print(f"Check interval: {status['check_interval']} seconds")
```

## Configuration

You can configure the process monitor behavior:

```python
from codesentinel.utils.process_monitor import start_monitor

# Check every 30 seconds (faster response, slightly more CPU usage)
monitor = start_monitor(check_interval=30)

# Check every 120 seconds (lower CPU usage, slower response)
monitor = start_monitor(check_interval=120)

# Disable monitoring entirely
monitor = start_monitor(enabled=False)
```

## How It Works

1. **Background Thread**: Runs a low-priority daemon thread
2. **Periodic Checks**: Wakes up every N seconds to check tracked processes
3. **Orphan Detection**:
   - Checks if tracked processes still exist
   - Verifies parent process ID matches
   - Terminates orphaned processes gracefully (SIGTERM)
   - Force kills if graceful termination fails (SIGKILL)
4. **Zombie Cleanup**:
   - Detects zombie/defunct child processes
   - Calls `os.waitpid()` to reap them
5. **Auto-Untracking**: Removes terminated processes from tracking list

## Performance Impact

- **CPU Usage**: Negligible (< 0.1% on average)
- **Memory Usage**: ~1-2 MB for daemon thread
- **Check Overhead**: ~10ms per check cycle
- **Default Interval**: 60 seconds (only 1 check per minute)

## Requirements

- Python 3.7+
- `psutil` library (automatically installed with CodeSentinel)

## Thread Safety

The ProcessMonitor is thread-safe and can be used in multi-threaded applications:

- Uses `threading.Lock` for tracked PIDs access
- Thread-safe start/stop operations
- Safe to call from multiple threads

## Error Handling

The monitor gracefully handles:

- Missing processes (already terminated)
- Access denied errors (insufficient permissions)
- Process no longer exists
- Monitor disabled or not started

## Example: Tracking Maintenance Tasks

```python
import subprocess
from codesentinel.utils.process_monitor import start_monitor, track_process

# Start monitor
monitor = start_monitor()

# Run maintenance task
proc = subprocess.Popen(['python', 'maintenance.py'])
track_process(proc.pid)

# If parent process crashes, the monitor will:
# 1. Detect the orphaned maintenance process
# 2. Terminate it gracefully
# 3. Prevent resource leaks
```

## Troubleshooting

### Monitor Not Starting

If you see "Warning: Process monitor not started", check:

1. Is `psutil` installed? `pip install psutil`
2. Python version >= 3.7
3. Check logs for detailed error message

### Processes Not Being Cleaned Up

If orphaned processes aren't being terminated:

1. Ensure `track_process()` was called for the PID
2. Check monitor is running: `get_monitor().get_status()`
3. Verify check interval isn't too long
4. Check process permissions (may need elevated privileges)

## Security Considerations

- **SECURITY FIRST**: Monitor only terminates tracked processes
- Never terminates arbitrary system processes
- Requires explicit tracking via `track_process()`
- Graceful termination (SIGTERM) before force kill (SIGKILL)
- Respects process ownership and permissions
