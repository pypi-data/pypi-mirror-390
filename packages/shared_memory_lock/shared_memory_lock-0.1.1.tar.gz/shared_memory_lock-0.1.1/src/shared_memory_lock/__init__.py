"""A multiprocessing lock implemented using shared memory and atomics."""

from .lock import SharedMemoryLock

__version__ = "0.1.1"

__all__ = [
    "SharedMemoryLock",
]
