"""
If Statements Exercise 3 (conditionals3.py)
This exercise focuses on compound and nested if statements (one level deep).
Follow the TODO instructions and fix any issues.
Uncomment and complete each section to pass all tests.
"""

# === COMPOUND IF STATEMENT FUNCTION ===
# TODO: Check if a number is within a specific range and if it's even

def check_number_properties(number):
    if number >= 1 and number <= 100 and number % 2 == 0:
        return "Number is within range and even"
    elif number >= 1 and number <= 100:
        return "Number is within range but odd"
    else:
        return "Number is out of range"

# === NESTED IF STATEMENT FUNCTION ===
# Solution: Check user role and permissions

def check_user_access(role, is_logged_in):
    if role == "admin":
        if is_logged_in:
            return "Admin access granted"
        else:
            return "Admin not logged in"
    elif role == "user":
        if is_logged_in:
            return "User access granted"
        else:
            return "User not logged in"
    else:
        return "Access denied"

# Call the functions with various inputs to test all conditions

# === TESTS ===
# Call the functions with various inputs to test all conditions

# Test check_number_properties
result_one = check_number_properties(50)
assert result_one == "Number is within range and even", f"[FAIL] Expected 'Number is within range and even', got '{result_one}'"

result_two = check_number_properties(45)
assert result_two == "Number is within range but odd", f"[FAIL] Expected 'Number is within range but odd', got '{result_two}'"

result_three = check_number_properties(150)
assert result_three == "Number is out of range", f"[FAIL] Expected 'Number is out of range', got '{result_three}'"

# Test check_user_access
result_four = check_user_access("admin", True)
assert result_four == "Admin access granted", f"[FAIL] Expected 'Admin access granted', got '{result_four}'"

result_five = check_user_access("admin", False)
assert result_five == "Admin not logged in", f"[FAIL] Expected 'Admin not logged in', got '{result_five}'"

result_six = check_user_access("user", True)
assert result_six == "User access granted", f"[FAIL] Expected 'User access granted', got '{result_six}'"

result_seven = check_user_access("user", False)
assert result_seven == "User not logged in", f"[FAIL] Expected 'User not logged in', got '{result_seven}'"

result_eight = check_user_access("guest", True)
assert result_eight == "Access denied", f"[FAIL] Expected 'Access denied', got '{result_eight}'"

print(f"\n{result_one}\n{result_two}\n{result_three}\n{result_four}\n{
    result_five}\n{result_six}\n{result_seven}\n{result_eight}.")