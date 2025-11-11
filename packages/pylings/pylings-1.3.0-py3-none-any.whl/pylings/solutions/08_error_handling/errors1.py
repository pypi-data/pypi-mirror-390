"""
Errors Exercise 1 (errors1.py)
This exercise introduces basic error handling in Python.
You will learn how to catch common runtime errors using try and except blocks.
Follow the TODO instructions and complete each section to pass all tests.
"""

# TODO: Handle the error, generically, when dividing two numbers
def safe_divide(a, b):
    # Attempt to divide a by b
    # If b is zero, catch the error and return "Cannot divide by zero!"
    try:
        return a / b
    except:
        return "Cannot divide by zero!"

    pass


# TODO: Handle the error, generically, when converting a string to an integer
def string_to_int(s):
    # Attempt to convert the string s to an integer
    # If conversion fails, return "Invalid integer input."
    try:
        return int(s)

    except:
        return "Invalid integer input"
    pass


# TODO: Handle the error, generically, when accessing a list element
def access_list_element(lst, index):
    # Attempt to return the element at the given index
    # If the index is out of range, return "Index out of range."
    # lst, has 5 indicies, refer to sample_list
    try:
        return lst[index]
    except:
        return "Index out of range"
    pass


# === TESTS ===
# DO NOT TOUCH 
# Testing safe_divide
result_one = safe_divide(10, 2)
assert result_one  == 5, "10 divided by 2 should return 5"

result_two = safe_divide(10, 0) 
assert result_two == "Cannot divide by zero!", f"Expected: Cannot divide by zero!, but got {result_two}"

# Testing string_to_int
result_three = string_to_int("123") 
assert result_three  == 123, f"Expected: String '123', but got {result_three}"

result_four = string_to_int("abc")
assert result_four == "Invalid integer input", f"Expected: Invalid integer input, but got {result_four}"

# Testing access_list_element
sample_list = [1, 2, 3, 4, 5]
result_five = access_list_element(sample_list, 2)
assert result_five == 3, f"Expected: 3, but got {result_five}"

result_six = access_list_element(sample_list, 10) 
assert result_six == "Index out of range", f"Expected: Index out of range, but got {result_six}"


print(f"{result_one}")
print(f"{result_two}")
print(f"{result_three}")
print(f"{result_four}")
print(f"{result_five}")
print(f"{result_six}")