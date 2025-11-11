"""
Threading Exercise 1 (threading1.py)
This program spawns multiple threads that each run for at least 1 second.
Each thread returns how much time it took to complete.
The program should wait until all the spawned threads have finished
and should collect their return values into a list.

Follow the TODO instructions and complete each section.
"""

import threading
import time

def worker(thread_id):
    """
    This function represents the work done by each thread.
    It should:
    - Record the start time
    - Sleep for 1 second
    - Print "Thread {thread_id} done"
    - Return the elapsed time
    """
    pass  # TODO: Implement worker function


def main():
    """
    The main function should:
    - Create and start 5 threads
    - Ensure all threads finish execution using `.join()`
    - Collect their return values in the `results` list
    """

    threads = []
    
    for i in range(5):
        # TODO: Spawn a new thread that runs `worker(i)`
        pass

    results = []

    for thread in threads:
        # TODO: Collect the results of all threads into the `results` list.
        pass

    if len(results) != 5:
        raise RuntimeError("Oh no! Some thread isn't done yet!")

    print()
    for i, result in enumerate(results):
        print(f"Thread {i} took {result:.2f} seconds")


if __name__ == "__main__":
    main()