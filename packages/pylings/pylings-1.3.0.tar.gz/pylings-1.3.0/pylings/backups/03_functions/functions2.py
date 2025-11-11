"""
Functions Exercise 2 (functions2.py)
This exercise introduces functions with parameters, return values, and basic operations.
Follow the TODO instructions and fix any issues.
Complete each section to pass all tests.
"""

# === FUNCTION WITH MULTIPLE PARAMETERS ===
# TODO: Define a function that multiplies two numbers and returns the result

def multiply_numbers():
    # TODO: Return the product of a and b
    pass

# === FUNCTION WITH DEFAULT PARAMETER ===
# TODO: Define a function that returns a greeting with an optional name parameter
# If no name is provided, default to "Guest"

def welcome_message():
    # TODO: Return a greeting message "Hello, name!" that includes the name
    pass

# === TESTS ===
# Call the functions with various inputs to test all conditions

# Test multiply_numbers function
result_one = multiply_numbers(3, 4)
assert result_one == 12, f"[FAIL] Expected 12, got '{result_one}'"

result_two = welcome_message("there")
assert result_two == "Hello, there!", f"[FAIL] Expected 'Hello, there!', got '{result_two}'"

result_three = welcome_message()
assert result_three == "Hello, Guest!", f"[FAIL] Expected 'Hello, Guest!', got '{result_three}'"

print(f"\n{result_one}\n{result_two}\{result_three}")