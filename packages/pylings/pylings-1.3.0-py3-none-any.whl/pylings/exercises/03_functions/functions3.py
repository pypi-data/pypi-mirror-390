"""
Functions Exercise 3 (functions3.py)
This exercise focuses on adding type hints and returning specific types.
"""

# TODO: Define a function that accepts an integer `year` and returns a string with a message like "The year is X."
def year_message(___ : ___) -> ___:
    pass

# TODO: Define a function that takes two floats and returns their average as a float
def average(___ : ___, ___ : ___) -> ___:
    pass

# === TESTS ===
import inspect

sig = inspect.signature(year_message)
params = sig.parameters

assert list(params.keys()) == ["year"], f"[FAIL] Function should have one parameter named 'year', but got {list(params.keys())}"
assert params["year"].annotation == int, f"[FAIL] Parameter 'year' should be of type int, but got {params["year"].annotation}"
assert sig.return_annotation == str, f"[FAIL] Function should return a string, but got {sig.return_annotation}"
assert year_message(2025) == "The year is 2025.", f"[FAIL] year_message failed, to  {year_message(2025)}"

sig = inspect.signature(average)
params = sig.parameters
assert list(params.keys()) == ["a", "b"], f"[FAIL] Function should have two parameters: 'a' and 'b', but got {params.keys()}"
assert all(p.annotation == float for p in params.values()), f"[FAIL] Both parameters should be of type float, [{params["a"].annotation}, {params["b"].annotation}]"
assert sig.return_annotation == float, f"[FAIL] Function should return a float, but got {sig.return_annotation}"
assert average(4.0, 6.0) == 5.0, f"[FAIL] average failed, got {average(4.0, 6.0)} should have been 5.0"

print(year_message(2025))
print(average(4.0, 6.0))