"""
Threading Exercise 2 (threading2.py)
This exercise introduces thread synchronization using `threading.Lock`.
Safely increment a shared counter using multiple threads.
Follow the TODO instructions and complete each section.
"""

import threading
import time

counter = 0  # Shared resource
lock = threading.Lock()  # TODO: Use this lock to prevent race conditions

# TODO: Define a function safe_increment that:
# - Uses `lock` to safely increment `counter` 1000 times
# - If lock is not used, race conditions may cause incorrect results
def safe_increment():
    pass


def main():
    """
    The main function should:
    - Create 5 threads that run `safe_increment`
    - Ensure all threads finish execution using `.join()`
    - Print the final value of `counter` (should be 5000 if correct)
    """

    global counter
    counter = 0  # Reset counter to ensure clean test runs

    threads = []

    for _ in range(5):
        # TODO: Spawn a new thread that runs `safe_increment`
        pass

    for thread in threads:
        # TODO: Ensure all threads finish execution
        pass

    print(f"Final counter value: {counter}")

    # Ensure correct synchronization was used
    assert counter == 5000, f"Error: Counter should be 5000, but got {counter}"


if __name__ == "__main__":
    main()