# Shared Queue

A high-performance shared-memory based multiprocessing queue for cross-process communication. Unlike `multiprocessing.Queue`, this queue is fully picklable, can be accessed by name from any process, and provides advanced features like batch operations and metrics.

## Features

- **Picklable**: Can be safely passed between processes via pickle
- **Named queues**: Multiple processes can connect to the same queue by name
- **Ring buffer design**: Efficient circular buffer with atomic head/tail pointers
- **Batch operations**: `put_batch()` for high-throughput scenarios
- **Shared memory backed**: Uses `multiprocessing.shared_memory` for zero-copy IPC
- **Thread and process safe**: Synchronized access with `shared_memory_lock`
- **Observable**: Built-in metrics for monitoring queue utilization
- **Run namespacing**: Isolate queues by run_id to prevent collisions

## Installation

```bash
pip install shared-multiprocess-queue
```

Or for development:

```bash
git clone <repo-url>
cd shared_queue
uv sync
uv pip install -e .
```

## Quick Start

```python
from shared_queue import SharedMemoryQueue
from multiprocessing import Process
import time

def worker(queue_name: str, run_id: str, worker_id: int):
    # Connect to existing queue by name
    queue = SharedMemoryQueue(name=queue_name, create=False, run_id=run_id)

    while True:
        try:
            task = queue.get(timeout=1.0)
            if task == "STOP":
                break
            print(f"Worker {worker_id} processing: {task}")
            time.sleep(0.1)  # Simulate work
        except queue.Empty:
            continue

    queue.close()

def main():
    run_id = "task_processor"

    # Create the queue in main process
    work_queue = SharedMemoryQueue(
        name="tasks",
        create=True,
        capacity=1000,
        item_size=4096,
        run_id=run_id
    )

    # Start worker processes
    workers = []
    for i in range(3):
        p = Process(target=worker, args=("tasks", run_id, i))
        p.start()
        workers.append(p)

    # Add tasks to queue
    for i in range(20):
        work_queue.put(f"task_{i}")

    # Signal workers to stop
    for _ in workers:
        work_queue.put("STOP")

    # Wait for workers to finish
    for p in workers:
        p.join()

    print(f"Final queue size: {work_queue.qsize()}")

    # Cleanup
    work_queue.unlink()

if __name__ == "__main__":
    main()
```

## API Reference

### `SharedMemoryQueue(name, create=False, capacity=1000, item_size=4096, run_id="", lock=None)`

Creates or connects to a shared memory queue.

**Parameters:**
- `name` (str): Queue identifier
- `create` (bool): Whether to create new queue (`True`) or connect to existing (`False`)
- `capacity` (int): Maximum number of items the queue can hold
- `item_size` (int): Maximum size of each serialized item in bytes
- `run_id` (str): Optional run identifier for namespacing queues
- `lock` (Any): Ignored - `SharedMemoryLock` is always used internally

**Methods:**
- `put(item, block=True, timeout=None)`: Add item to queue
- `get(block=True, timeout=None)`: Remove and return item from queue
- `put_nowait(item)`: Add item without blocking (raises `Full` if queue is full)
- `get_nowait()`: Get item without blocking (raises `Empty` if queue is empty)
- `put_batch(items)`: Add multiple items atomically
- `empty()`: Check if queue is empty
- `full()`: Check if queue is full
- `qsize()`: Get approximate queue size
- `get_metrics()`: Return queue metrics dictionary
- `close()`: Close connection to shared memory
- `unlink()`: Delete the shared memory segment (call from creator process)

**Exceptions:**
- `Empty`: Raised when queue is empty and non-blocking operation requested
- `Full`: Raised when queue is full and non-blocking operation requested

## Advanced Usage

### Batch Operations

For high-throughput scenarios, use `put_batch()` to add multiple items atomically:

```python
queue = SharedMemoryQueue("batch_queue", create=True, capacity=10000)

# Process items in batches for better performance
batch = []
for i in range(100):
    batch.append(f"item_{i}")
    if len(batch) >= 50:
        queue.put_batch(batch)
        batch = []

# Don't forget remaining items
if batch:
    queue.put_batch(batch)
```

### Queue Metrics

Monitor queue performance with built-in metrics:

```python
queue = SharedMemoryQueue("monitored_queue", create=True, capacity=1000)

# Add some items
for i in range(100):
    queue.put(f"item_{i}")

metrics = queue.get_metrics()
print(f"Queue size: {metrics['queue_size']}")
print(f"Capacity: {metrics['queue_capacity']}")
print(f"Utilization: {metrics['queue_utilization_percent']:.1f}%")
print(f"Item size limit: {metrics['queue_item_size_bytes']} bytes")
```

### Cross-Process Communication

```python
# Producer process
def producer(queue_name, run_id):
    queue = SharedMemoryQueue(queue_name, create=False, run_id=run_id)
    for i in range(1000):
        queue.put({"data": f"item_{i}", "timestamp": time.time()})
    queue.put(None)  # Sentinel value

# Consumer process
def consumer(queue_name, run_id):
    queue = SharedMemoryQueue(queue_name, create=False, run_id=run_id)
    results = []
    while True:
        item = queue.get()
        if item is None:  # Sentinel value
            break
        results.append(item)
    return results

# Main process
run_id = "data_pipeline"
queue = SharedMemoryQueue("data_queue", create=True, capacity=2000, run_id=run_id)

# Start processes
p1 = Process(target=producer, args=("data_queue", run_id))
p2 = Process(target=consumer, args=("data_queue", run_id))

p1.start()
p2.start()

p1.join()
p2.join()

queue.unlink()
```

### Timeout Handling

```python
queue = SharedMemoryQueue("timeout_queue", create=True, capacity=10)

try:
    # Will wait up to 5 seconds for space
    queue.put("item", block=True, timeout=5.0)
except Full:
    print("Queue was full for 5 seconds")

try:
    # Will wait up to 2 seconds for an item
    item = queue.get(block=True, timeout=2.0)
except Empty:
    print("No items available for 2 seconds")
```

## Performance Characteristics

- **Ring buffer**: O(1) put/get operations
- **Zero-copy**: Items stored directly in shared memory
- **Atomic operations**: Thread and process-safe without Python GIL limitations
- **Batch operations**: Minimize lock contention for high-throughput scenarios
- **Configurable capacity**: Balance memory usage vs queue depth

## Use Cases

### 1. High-Throughput Task Distribution

```python
# Distribute work across multiple worker processes
task_queue = SharedMemoryQueue("tasks", create=True, capacity=50000, item_size=8192)

# Producer adds tasks
tasks = generate_large_task_list()
task_queue.put_batch(tasks)  # Efficient batch insertion

# Multiple workers consume tasks
def worker():
    while True:
        try:
            task = task_queue.get_nowait()
            process_task(task)
        except Empty:
            time.sleep(0.01)
```

### 2. Inter-Service Communication

```python
# Service A publishes events
event_queue = SharedMemoryQueue("events", create=True, capacity=10000, run_id="system")

# Service B subscribes to events
event_queue = SharedMemoryQueue("events", create=False, run_id="system")
while True:
    event = event_queue.get()
    handle_event(event)
```

### 3. Real-Time Data Processing

```python
# High-frequency data ingestion
data_queue = SharedMemoryQueue("sensor_data", create=True, capacity=100000, item_size=1024)

# Sensor data producer
def collect_sensor_data():
    batch = []
    while True:
        reading = read_sensor()
        batch.append(reading)
        if len(batch) >= 100:  # Batch for efficiency
            data_queue.put_batch(batch)
            batch = []
```

## Implementation Details

- Uses `multiprocessing.shared_memory` for the underlying storage
- Ring buffer layout: `[head][tail][capacity][item_size][data_slots...]`
- Items serialized with `cloudpickle` for maximum compatibility
- Synchronized with `shared_memory_lock` for cross-process safety
- Header stores 64-bit integers for head/tail pointers
- Each slot prefixed with 32-bit length for variable-size items

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=shared_queue

# Type checking
uv run mypy .

# Linting
uv run ruff check .
```

## License

MIT