"""
Loops Exercise 1 (loops1.py)
This exercise introduces basic looping constructs in Python: for loops and while loops.
Follow the TODO instructions and fix any issues.
Complete each section to pass all tests.
"""

# === FOR LOOP ===
# Solution: Write a function that returns a list of numbers from 1 to n using a for loop

def generate_numbers(n):
    numbers = []
    for i in range(1, n + 1):
        numbers.append(i)
    return numbers

# === WHILE LOOP ===
# Solution: Write a function that sums numbers from 1 to n using a while loop

def sum_numbers(n):
    total = 0
    current = 1
    while current <= n:
        total += current
        current += 1
    return total

# === LOOP WITH CONDITIONALS ===
# Solution: Write a function that returns a list of even numbers from 1 to n using a loop and condition

def even_numbers(n):
    evens = []
    for i in range(1, n + 1):
        if i % 2 == 0:
            evens.append(i)
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