import threading
import time
from functools import wraps


class RateLimiter:
    """Simple thread-safe rate limiter.

    Allows up to ``max_calls_per_second``.
    """

    def __init__(self, max_calls_per_second: float):
        """Initialize with the maximum allowed calls per second."""
        self.max_calls_per_second = max_calls_per_second
        self.lock = threading.Lock()
        self.calls = []

    def __call__(self, func):
        """Decorate a function to enforce rate limits."""
        min_interval = 1.0 / self.max_calls_per_second

        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                now = time.time()
                self.calls = [t for t in self.calls if now - t < 1.0]

                if self.calls:
                    elapsed = now - self.calls[-1]
                    sleep_time = min_interval - elapsed
                    if sleep_time > 0:
                        time.sleep(sleep_time)

                self.calls.append(time.time())

            return func(*args, **kwargs)

        return wrapper
