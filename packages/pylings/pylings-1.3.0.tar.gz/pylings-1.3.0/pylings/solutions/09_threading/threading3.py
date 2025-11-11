"""
Threading Exercise 3 (threading3.py)
This exercise introduces `threading.Semaphore` for resource management.
Limit concurrent access to a resource using a semaphore.
"""

import threading
import time

semaphore = threading.Semaphore(3)  # Limit concurrent access to 3 threads
active_threads = 0  # Track active threads
active_threads_lock = threading.Lock()  # Lock to modify active_threads safely
max_threads_reached = 0  # Track the highest number of concurrent threads

def access_resource(thread_id):
    """
    Function to control concurrent access to a resource:
    - Acquires the semaphore before proceeding.
    - Safely increments `active_threads` inside `active_threads_lock`.
    - Ensures no more than 3 threads are active at a time.
    - Prints `"Thread {thread_id} accessing resource"`.
    - Sleeps for 0.1 seconds to simulate work.
    - Prints `"Thread {thread_id} done"`.
    - Safely decrements `active_threads` and releases the semaphore.
    """
    global active_threads, max_threads_reached

    with semaphore:  # Acquire semaphore (ensures max 3 threads run concurrently)
        with active_threads_lock:
            active_threads += 1
            max_threads_reached = max(max_threads_reached, active_threads)
            assert active_threads <= 3, f"Error: More than 3 threads running at once! Current: {active_threads}"

        print(f"Thread {thread_id} accessing resource")
        time.sleep(0.1)  # Simulate work
        print(f"Thread {thread_id} done")

        with active_threads_lock:
            active_threads -= 1  # Decrement active threads


def main():
    """
    The main function:
    - Creates 6 threads that run `access_resource`
    - Ensures all threads finish execution using `.join()`
    - Verifies that no more than 3 threads access the resource at the same time
    """

    global active_threads, max_threads_reached
    active_threads = 0  # Reset counter before running
    max_threads_reached = 0  # Reset max tracking

    threads = []

    for i in range(6):
        thread = threading.Thread(target=access_resource, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()  # Ensures all threads complete execution

    # Ensure active_threads is back to zero
    assert active_threads == 0, f"Error: active_threads should be 0 after execution, but got {active_threads}"

    # Ensure max concurrent threads never exceeded 3
    assert max_threads_reached <= 3 and max_threads_reached > 0, f"Error: More than 3 threads ran concurrently! Max observed: {max_threads_reached}"


if __name__ == "__main__":
    main()