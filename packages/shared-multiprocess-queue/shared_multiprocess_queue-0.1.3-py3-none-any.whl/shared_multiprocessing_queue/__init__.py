"""A shared-memory based multiprocessing queue for cross-process communication"""

from .queue import Empty, Full, SharedMemoryQueue

__version__ = "0.1.3"
__all__ = ["SharedMemoryQueue", "Empty", "Full"]
