# Shared Memory Lock

A multiprocessing lock implemented using shared memory and atomics.

## Installation

```bash
uv pip install -e .
```

## Usage

```python
from shared_memory_lock import SharedMemoryLock

# Create a lock (first process)
lock = SharedMemoryLock(name="my_lock", create=True, run_id="app1")

# Connect to the same lock (other processes)
lock = SharedMemoryLock(name="my_lock", create=False, run_id="app1")

# Use as context manager
with lock:
    # Critical section - only one process can be here
    print("Doing important work...")

# Or manual acquire/release
if lock.acquire(blocking=False):
    try:
        # Got the lock
        print("Acquired lock!")
    finally:
        lock.release()
else:
    print("Could not acquire lock")

# Clean up when done
lock.close()
lock.unlink()  # Only call from one process
```

## Features

- **Cross-process synchronization**: Works across multiple processes
- **Atomic operations**: Uses real atomic compare-and-swap for mutual exclusion
- **Picklable**: Can be passed to multiprocessing.Process
- **Context manager**: Supports `with` statements
- **Non-blocking**: Optional non-blocking acquire with timeout

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run --python 3.13.7 pytest 

# Run tests with coverage
uv run --python 3.13.7 pytest --cov=shared_memory_lock
```

## License

MIT