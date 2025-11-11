"""A shared-memory based multiprocessing queue for cross-process communication"""

from .queue import SharedMemoryQueue, Empty, Full

__version__ = "0.1.1"
__all__ = ["SharedMemoryQueue", "Empty", "Full"]