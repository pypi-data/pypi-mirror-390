"""
If Statements Exercise 1 (conditionals1.py)
This exercise introduces basic if statements and comparison operations in Python.
Follow the TODO instructions and fix any issues.
Uncomment and complete each section to pass all tests.
Try experimenting with different comparison operators: ==, !=, <, <=, >, >=
"""

# === COMPARISON FUNCTIONS ===
# TODO: Fill in the correct comparison operators in each function

def is_equal(a, b):
    if a __ b:
        return "a is equal to b"
    else:
        return "a is not equal to b"

def is_not_equal(a, b):
    if a __ b:
        return "a is not equal to b"
    else:
        return "a is equal to b"

def is_less_than(a, b):
    if a __ b:
        return "a is less than b"
    else:
        return "a is not less than b"

def is_less_than_or_equal(a, b):
    if a __ b:
        return "a is less than or equal to b"
    else:
        return "a is greater than b"

def is_greater_than(a, b):
    if a __ b:
        return "a is greater than b"
    else:
        return "a is not greater than b"

def is_greater_than_or_equal(a, b):
    if a __ b:
        return "a is greater than or equal to b"
    else:
        return "a is less than b"

# === TESTS ===
# Call the comparison functions with various inputs to test all comparison cases

# Test equal
result_one = is_equal(10, 10)
assert result_one == "a is equal to b", f"[FAIL] Expected 'a is equal to b', got '{result_one}'"

# Test not equal
result_two = is_not_equal(10, 5)
assert result_two == "a is not equal to b", f"[FAIL] Expected 'a is not equal to b', got '{result_two}'"

# Test less than
result_three = is_less_than(5, 10)
assert result_three == "a is less than b", f"[FAIL] Expected 'a is less than b', got '{result_three}'"

# Test less than or equal
result_four = is_less_than_or_equal(10, 20)
assert result_four == "a is less than or equal to b", f"[FAIL] Expected 'a is less than or equal to b', got '{result_four}'"

# Test greater than
result_five = is_greater_than(20, 10)
assert result_five == "a is greater than b", f"[FAIL] Expected 'a is greater than b', got '{result_five}'"

# Test greater than or equal
result_six = is_greater_than_or_equal(20, 20)
assert result_six == "a is greater than or equal to b", f"[FAIL] Expected 'a is greater than or equal to b', got '{result_six}'"

print(f"\n{result_one}\n{result_two}\n{result_three}\n{result_four}\n{result_five}\n{result_six}.")