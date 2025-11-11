"""
Conditionals Exercise 4 (conditionals4.py)
This exercise introduces the use of match-case (Python's structural pattern matching).
Available from Python 3.10 onwards.
"""

# TODO: Define a function `http_status` that takes an integer `code` and returns a string message.
# Use match-case to return the following:
# - 200: "OK"
# - 301: "Moved Permanently"
# - 404: "Not Found"
# - 500: "Internal Server Error"
# - Any other value: "Unknown Status"

def http_status(code: int) -> str:
    pass

# === TESTS ===
import inspect

sig = inspect.signature(http_status)
params = sig.parameters

assert list(params.keys()) == ["code"], f"[FAIL] Function should take one parameter 'code'"
assert params["code"].annotation == int, f"[FAIL] 'code' should be of type int"
assert sig.return_annotation == str, f"[FAIL] Function should return a string"

assert http_status(200) == "OK", "[FAIL] Expected 'OK'"
assert http_status(301) == "Moved Permanently", "[FAIL] Expected 'Moved Permanently'"
assert http_status(404) == "Not Found", "[FAIL] Expected 'Not Found'"
assert http_status(500) == "Internal Server Error", "[FAIL] Expected 'Internal Server Error'"
assert http_status(123) == "Unknown Status", "[FAIL] Expected 'Unknown Status'"

print("All tests passed!")
