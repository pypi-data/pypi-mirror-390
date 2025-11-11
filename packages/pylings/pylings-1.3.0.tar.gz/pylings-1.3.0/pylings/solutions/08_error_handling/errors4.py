"""
Errors Exercise 4 (errors4.py)
This exercise introduces custom exceptions.
Create and raise their own exception classes.
Follow the TODO instructions and complete each section to pass all tests.
"""

# Custom exception for negative numbers
class NegativeNumberError(Exception):
    """Raised when a negative number is provided."""
    pass

def validate_positive(number):
    if number < 0:
        raise NegativeNumberError("Negative numbers are not allowed.")
    return number


# Custom exception for invalid age
class InvalidAgeError(Exception):
    """Raised when an invalid age is provided."""
    pass

def check_age(age):
    if age < 0 or age > 120:
        raise InvalidAgeError("Invalid age.")
    return "Age is valid."


# Custom exception for insufficient funds
class InsufficientFundsError(Exception):
    """Raised when an account does not have enough balance for withdrawal."""
    pass

def withdraw_money(balance, amount):
    if amount > balance:
        raise InsufficientFundsError("Insufficient funds.")
    return "Transaction successful."


# Tests to check if your code works
# Testing validate_positive
try:
    result_one = validate_positive(-5)
except NegativeNumberError as e:
    result_one = str(e)
    assert result_one == "Negative numbers are not allowed.", f"Expected: Negative numbers are not allowed., but got {result_one}"

result_two = validate_positive(10)
assert result_two == 10, "Positive numbers should be returned as is."

# Testing check_age
try:
    result_three = check_age(130)
except InvalidAgeError as e:
    result_three = str(e)
    assert result_three == "Invalid age.", f"Expected: Invalid age., but got {result_three}"

result_four = check_age(25)
assert result_four == "Age is valid.", "Valid age should return confirmation message."

# Testing withdraw_money
try:
    result_five = withdraw_money(50, 100)
except InsufficientFundsError as e:
    result_five = str(e)
    assert result_five == "Insufficient funds.", f"Expected: Insufficient funds., but got {result_five}"

result_six = withdraw_money(200, 100)
assert result_six == "Transaction successful.", "Sufficient funds should allow withdrawal."

# Print results for visibility
print(result_one)
print(result_two)
print(result_three)
print(result_four)
print(result_five)
print(result_six)