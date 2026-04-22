import hashlib
from typing import Any


def hash_key(*values: Any) -> str:
    """
    Generate a consistent hash key from multiple values.
    
    Useful for Kafka partition keys to co-locate related events.
    """
    combined = "".join(str(v) for v in values)
    return hashlib.sha256(combined.encode()).hexdigest()
