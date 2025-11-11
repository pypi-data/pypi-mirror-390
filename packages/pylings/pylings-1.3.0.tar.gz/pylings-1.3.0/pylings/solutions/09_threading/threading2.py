"""
Threading Exercise 2 (threading2.py)
This exercise introduces thread synchronization using `threading.Lock`.
Safely increment a shared counter using multiple threads.
"""

import threading

counter = 0  # Shared resource
lock = threading.Lock()  # Lock to prevent race conditions

def safe_increment():
    """
    Function to safely increment the shared counter 1000 times.
    Uses a lock to ensure thread-safe modification.
    """
    global counter
    for _ in range(1000):
        with lock:  # Ensures only one thread modifies `counter` at a time
            counter += 1


def main():
    """
    The main function:
    - Creates 5 threads that run `safe_increment`
    - Ensures all threads finish execution using `.join()`
    - Prints the final value of `counter` (should be 5000 if correct)
    """

    global counter
    counter = 0  # Reset counter before running

    threads = []

    for _ in range(5):
        thread = threading.Thread(target=safe_increment)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()  # Ensures all threads complete execution

    print(f"Final counter value: {counter}")

    # Validation: Ensure counter is exactly 5000
    assert counter == 5000, f"Error: Counter should be 5000, but got {counter}"

if __name__ == "__main__":
    main()