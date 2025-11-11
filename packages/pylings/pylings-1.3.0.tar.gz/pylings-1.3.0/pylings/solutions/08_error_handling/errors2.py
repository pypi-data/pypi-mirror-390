"""
Errors Exercise 2 (errors2.py)
This exercise expands on errors1 by using explicit error handling.
Instead of returning a string, return the actual exception type.
Use `type(exception)` to compare with expected exceptions.
Refer to: https://docs.python.org/3/library/exceptions.html
Follow the TODO instructions and complete each section to pass all tests.
"""

# TODO: Ensure the function returns the correct exception type
# Implement each function to return the actual exception type

# TODO: Catch the correct error when dividing by zero
def catch_zero_division(a, b):
    try:
        return a / b
    except:
        return ZeroDivisionError  # TODO: Return the actual exception type


# TODO: Catch the correct error when converting an invalid string to an integer
def catch_value_error(value):
    try:
        return int(value)
    except:
        return ValueError  # TODO: Return the actual exception type


# TODO: Catch the correct error when accessing an invalid list index
def catch_index_error(lst, index):
    try:
        return lst[index]
    except:
        return IndexError  # TODO: Return the actual exception type


# TODO: Catch the correct errorwhen accessing a non-existent dictionary key
def catch_key_error(dictionary, key):
    try:
        return dictionary[key]
    except:
        return KeyError  # TODO: Return the actual exception type

# DO NOT TOUCH #
# This function demonstrates a generic exception handler
# With the use of type(), we can return the type from generic exception
def generic_exception(a, b):
    try: 
        return  b / c
    except Exception as e:
        print(f"Exception: {type(e)}")
    pass

generic_exception(1, 0)  # Should print an exception message

# Tests to check if your functions work
# The return value should match the actual exception type

# Testing catch_zero_division
result_one = catch_zero_division(1, 0)
assert result_one == ZeroDivisionError, f"Expected: ZeroDivisionError, but got {result_one}"

# Testing catch_value_error
result_two = catch_value_error("abc")
assert result_two == ValueError, f"Expected: ValueError, but got {result_two}"

# Testing catch_index_error
sample_list = [1, 2, 3]
result_three = catch_index_error(sample_list, 5)
assert result_three == IndexError, f"Expected: IndexError, but got {result_three}"

# Testing catch_key_error
sample_dict = {"name": "Alice"}
result_four = catch_key_error(sample_dict, "age")
assert result_four == KeyError, f"Expected: KeyError, but got {result_four}"


print(f"Exception: {result_one}")
print(f"Exception: {result_two}")
print(f"Exception: {result_three}")
print(f"Exception: {result_four}")