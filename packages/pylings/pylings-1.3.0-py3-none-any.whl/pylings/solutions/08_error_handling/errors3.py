"""
Errors Exercise 3 (errors3.py)
This exercise introduces raising exceptions with `raise` and using `finally` to ensure cleanup.
Follow the TODO instructions and complete each section to pass all tests.
"""

# Raise a ValueError if the input number is negative
def check_positive(number):
    if number < 0:
        raise ValueError("Number must be positive")
    return number


# Raise a TypeError if inputs are not both integers
def add_integers(a, b):
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Inputs must be integers")
    return a + b


# Use a finally block to ensure a file is always closed
def safe_file_read(filename):
    try:
        file = open(filename, "r")
        content = file.read()
        return content
    except FileNotFoundError:
        return "File not found."
    finally:
        try:
            file.close()
        except NameError:
            pass  # File was never opened, so we do nothing

# Tests to check if your code works
# Testing check_positive
try:
    result_one = check_positive(-5)
except ValueError as e:
    result_one = str(e)
    assert result_one == "Number must be positive", f"Expected ValueError: Number must be positive, but got {result_one}"

result_two = check_positive(10)
assert result_two == 10, "Positive numbers should be returned as is."

# Testing add_integers
try:
    result_three = add_integers(10, "five")
except TypeError as e:
    result_three = str(e)
    assert result_three == "Inputs must be integers", f"Expected TypeError: Inputs must be integers, but got {result_three}"

result_four = add_integers(4, 6)
assert result_four == 10, "4 + 6 should return 10"

# Testing safe_file_read
result_five = safe_file_read("missing_file.txt")
assert  result_five == "File not found.", f"Expected: File not found. But got, {result_five}"

print(result_one)
print(result_two)
print(result_three)
print(result_four)
print(result_five)