"""
Threading Exercise 3 (threading3.py)
This exercise introduces `threading.Semaphore` for resource management.
Limit concurrent access to a resource using a semaphore.
Follow the TODO instructions and complete each section.
"""

import threading
import time

semaphore = threading.Semaphore(3)  # TODO: Limit concurrent access to 3 threads

def access_resource(thread_id):
    """
    This function should:
    - Wait for access using `semaphore.acquire()`
    - Print "Thread {thread_id} accessing resource"
    - Sleep for 0.1 seconds to simulate work
    - Print "Thread {thread_id} done"
    - Release the semaphore after work is done
    """
    pass  # TODO: Implement function logic


def main():
    """
    The main function should:
    - Create 6 threads that run `access_resource`
    - Ensure all threads finish execution using `.join()`
    - Verify that no more than 3 threads access the resource at the same time
    """

    threads = []

    for i in range(6):
        # TODO: Spawn a new thread that runs `access_resource(i)`
        pass

    for thread in threads:
        # TODO: Ensure all threads finish execution
        pass

if __name__ == "__main__":
    main()