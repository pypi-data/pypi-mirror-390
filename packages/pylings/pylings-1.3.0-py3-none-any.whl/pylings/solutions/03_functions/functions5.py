"""
Functions Exercise 5 (functions5.py)
This exercise introduces returning multiple values from a function using tuples.
"""

# TODO: Define a function `basic_stats` that takes two numbers and returns:
# (1) their sum, (2) their product, and (3) their average
# Return these three values as a tuple

def basic_stats(a: float, b: float) -> tuple:
    return (a + b, a * b, (a + b) / 2)

# === TESTS ===
import inspect

sig = inspect.signature(basic_stats)
params = sig.parameters

assert list(params.keys()) == ["a", "b"], f"[FAIL] Function should have two parameters 'a' and 'b', got {list(params.keys())}"
assert all(p.annotation == float for p in params.values()), f"[FAIL] Parameters should be floats, got {[p.annotation for p in params.values()]}"
assert sig.return_annotation == tuple, f"[FAIL] Function should return a tuple"

sum_, product, average = basic_stats(4.0, 2.0)
assert sum_ == 6.0, f"[FAIL] Sum incorrect, got {sum_}"
assert product == 8.0, f"[FAIL] Product incorrect, got {product}"
assert average == 3.0, f"[FAIL] Average incorrect, got {average}"

print(f"Sum: {sum_}, Product: {product}, Average: {average}")