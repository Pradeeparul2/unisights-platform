import time


def now_ms() -> int:
    """
    Current timestamp in milliseconds.
    """
    return int(time.time() * 1000)
