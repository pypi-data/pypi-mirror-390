"""
Threading Exercise 1 (threading1_solution.py)
This program spawns multiple threads that each run for at least 1 second.
Each thread returns how much time it took to complete.
The program waits until all threads finish execution and collects their return values.
"""

import threading
import time

def worker(thread_id):
    """
    Worker function:
    - Records the start time
    - Sleeps for 1 second
    - Prints "Thread {thread_id} done"
    - Returns the elapsed time
    """
    start_time = time.time()
    time.sleep(1)
    print(f"Thread {thread_id} done")
    return time.time() - start_time


def main():
    """
    The main function:
    - Creates and starts 5 threads
    - Ensures all threads finish execution using `.join()`
    - Collects their return values in the `results` list
    """

    threads = []
    results = []

    for i in range(5):
        thread = threading.Thread(target=lambda i=i: results.append(worker(i)))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    if len(results) != 5:
        raise RuntimeError("Oh no! Some thread isn't done yet!")

    print()
    for i, result in enumerate(results):
        print(f"Thread {i} took {result:.2f} seconds")


if __name__ == "__main__":
    main()