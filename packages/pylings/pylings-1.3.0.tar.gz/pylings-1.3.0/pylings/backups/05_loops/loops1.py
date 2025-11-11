"""
Loops Exercise 1 (loops1.py)
This exercise introduces basic looping constructs in Python: for loops and while loops.
Follow the TODO instructions and fix any issues.
Uncomment and complete each section to pass all tests.
"""

# === FOR LOOP ===
# TODO: Modify the function so that it returns a list of numbers from 1 to n using a for loop

def generate_numbers(n):
    numbers = []
    # TODO: Use a for loop to append numbers from 1 to n to the list
    pass
    return numbers

# === WHILE LOOP ===
# TODO: Modify the function so that it sums numbers from 1 to n using a while loop and returns the total

def sum_numbers(n):
    total = 0
    current = 1
    # TODO: Use a while loop to add numbers from 1 to n
    pass
    return total

# === LOOP WITH CONDITIONALS ===
# TODO: Modify the function so that it returns a list of even numbers from 1 to n using a loop and condition

def even_numbers(n):
    evens = []
    # TODO: Use a loop and if condition to collect even numbers
    pass
    return evens

# === TESTS ===
# Call the functions with various inputs to test all conditions

# Test generate_numbers function
result_one = generate_numbers(5)
assert result_one == [1, 2, 3, 4, 5], f"[FAIL] Expected [1, 2, 3, 4, 5], got '{result_one}'"

# Test sum_numbers function
result_two = sum_numbers(5)
assert result_two == 15, f"[FAIL] Expected 15, got '{result_two}'"

# Test even_numbers function
result_three = even_numbers(10)
assert result_three == [2, 4, 6, 8, 10], f"[FAIL] Expected [2, 4, 6, 8, 10], got '{result_three}'"

print(f"\n{result_one}\n{result_two}\n{result_three}\n")