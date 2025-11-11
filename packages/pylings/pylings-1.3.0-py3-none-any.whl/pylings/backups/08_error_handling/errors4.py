"""
Errors Exercise 4 (errors4.py)
This exercise introduces custom exceptions.
Create and raise their own exception classes.
Follow the TODO instructions and complete each section to pass all tests.
"""

# TODO: Define a custom exception called NegativeNumberError
# This exception should inherit from Exception


# TODO: Define a function validate_positive that raises NegativeNumberError
# if the input number is negative
def validate_positive(number):
    # If number is negative, raise NegativeNumberError with message "Negative numbers are not allowed."
    pass


# TODO: Define a custom exception called InvalidAgeError
# This exception should inherit from Exception


# TODO: Define a function check_age that raises InvalidAgeError
# if age is below 0 or greater than 120
def check_age(age):
    # If age is below 0 or above 120, raise InvalidAgeError with message "Invalid age."
    pass


# TODO: Define a function withdraw_money that raises a custom InsufficientFundsError
# if withdrawal amount exceeds balance
class InsufficientFundsError(Exception):
    pass


def withdraw_money(balance, amount):
    # If amount > balance, raise InsufficientFundsError with message "Insufficient funds."
    pass


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