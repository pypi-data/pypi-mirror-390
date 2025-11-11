# Threading Exercises

These exercises introduce multithreading in Python using the `threading` module. You'll learn to create threads, safely share data, and manage concurrent access to resources.

---

## Covered Topics

| Exercise         | Concept                                             |
|------------------|-----------------------------------------------------|
| `threading1.py`  | Spawning and joining threads, capturing return values |
| `threading2.py`  | Synchronization using `threading.Lock`              |
| `threading3.py`  | Resource control using `threading.Semaphore`        |

---

## How to Use

Each file includes:
- A multi-threaded problem to solve
- Clear `TODO` instructions
- Tests using `assert` to verify thread-safe and correct execution

---

## Tips
- Always `.join()` threads to ensure completion before moving on
- Use `Lock` when modifying shared variables to avoid race conditions
- Use `Semaphore` to control the maximum number of threads accessing a resource
- Shared variables should be marked `global` when modified inside threads

---

## Bonus Ideas
- Use `concurrent.futures.ThreadPoolExecutor` for easier thread management
- Add timing and logging to understand performance
- Simulate file access or network requests to test concurrency models

---

Thread safely. Think concurrently.