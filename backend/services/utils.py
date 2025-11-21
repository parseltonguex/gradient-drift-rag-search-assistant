import time
import json
from datetime import datetime

# -----------------------------------------------------------
# FUNCTION: Timing Decorator
# -----------------------------------------------------------
def time_it(func):
    """
    Simple decorator to measure execution time of a function.
    Usage:
        @time_it
        def some_function():
            ...
    """
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = round((time.time() - start) * 1000, 2)
        print(f"[TIMER] {func.__name__} executed in {duration} ms")
        return result
    return wrapper


# -----------------------------------------------------------
# FUNCTION: Save JSONL Log Entry
# -----------------------------------------------------------
def append_jsonl(file_path: str, record: dict):
    """
    Append a single JSON record to a .jsonl file.
    Creates the file if it doesn't exist.
    """
    with open(file_path, "a") as f:
        f.write(json.dumps(record) + "\n")


# -----------------------------------------------------------
# FUNCTION: Timestamp Generator
# -----------------------------------------------------------
def utc_timestamp() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.utcnow().isoformat()
