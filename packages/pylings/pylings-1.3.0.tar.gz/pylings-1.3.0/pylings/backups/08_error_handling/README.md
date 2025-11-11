# Error Handling Exercises

These exercises guide you through Python’s error handling system, from simple `try`/`except` blocks to custom exception classes. You'll learn how to write safer and more robust code that anticipates and handles runtime issues.

---

## Covered Topics

| Exercise         | Concept                                        |
|------------------|------------------------------------------------|
| `errors1.py`     | Basic error handling with `try`/`except`       |
| `errors2.py`     | Identifying and returning specific exception types |
| `errors3.py`     | Using `raise`, `finally`, and validating inputs|
| `errors4.py`     | Defining and using custom exception classes     |

---

## How to Use

Each file contains:
- Function stubs with `TODO` comments
- Built-in test cases using `assert`

If everything is correct, you'll see all expected output with no `[FAIL]` messages.

---

## Tips
- Use `try/except` to catch potential runtime errors
- Always be specific when catching exceptions (`ValueError`, `KeyError`, etc.)
- Use `raise` to throw exceptions when something isn’t valid
- The `finally` block always executes — useful for cleanup (like closing files)
- Custom exceptions should inherit from `Exception`

---

Have fun!