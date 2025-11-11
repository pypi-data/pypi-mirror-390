"""
Functions Exercise 1 (functions1.py)
This exercise introduces the basics of defining and calling functions in Python.
Follow the TODO instructions and fix any issues.
Complete each section to pass all tests.
"""

# === BASIC FUNCTION DEFINITION ===
# TODO: Modify the function greet(), so that it takes no arguments and returns the string "Hello, World!"

def greet():
    pass

# TODO: Define a function called farewell, that takes no argument and returns the string "Goodbye!"

# === TESTS ===
# Call the functions with various inputs to test all conditions

result_one = greet()
assert result_one == "Hello, World!", f"[FAIL] Expected 'Hello, World!', got '{result_one}'"

result_two = farewell()
assert result_two == "Goodbye!", f"[FAIL] Expected 'Goodbye!', got '{result_two}'"

print(f"\n{result_one}\n{result_two}")