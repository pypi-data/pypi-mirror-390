"""
Variables Exercise 3 (variables3.py)
This exercise focuses on string concatenation, different ways to combine variables, and string multiplication.
Follow the TODO instructions and fix any issues.
Uncomment and complete each section to pass all tests.
"""

# === BASIC STRING CONCATENATION ===
# Solution: Combine first_name and last_name into full_name using concatenation

first_name = "John"
last_name = "Cleese"
full_name = first_name + " " + last_name  # Concatenate first_name and last_name with a space in between

# === CONCATENATION WITH NUMBERS ===
# Solution: Convert number to string and concatenate with a message

age = 50
message = "I am " + str(age) + " years old."  # Convert age to string and concatenate

# === CONCATENATION USING F-STRINGS ===
# Solution: Use an f-string to format a message with name and age

f_string_message = f"{full_name} is {age} years old."

# === CONCATENATION USING .FORMAT() ===
# Solution: Use .format() method to create a message

format_message = "{} is {} years old.".format(full_name, age)

# === STRING MULTIPLICATION ===
# Solution: Repeat a string multiple times using the * operator

repeat_word = "Hello"
multiplied_string = repeat_word * 3  # Repeat "Hello" 3 times

# === TESTS ===
# Call the variables to test concatenation methods

assert full_name == "John Cleese", f"[FAIL] Expected 'John Cleese', got '{full_name}'"
assert message == "I am 50 years old.", f"[FAIL] Expected 'I am 50 years old.', got '{message}'"
assert f_string_message == "John Doe is 50 years old.", f"[FAIL] Expected 'John Doe is 50 years old.', got '{f_string_message}'"
assert format_message == "John Doe is 50 years old.", f"[FAIL] Expected 'John Doe is 50 years old.', got '{format_message}'"
assert multiplied_string == "HelloHelloHelloHelloHelloHelloHelloHelloHello", f"[FAIL] Expected 'HelloHelloHelloHelloHelloHelloHelloHelloHello', got '{multiplied_string}'"

print(f"{full_name}")
print(f"{message}")
print(f"{f_string_message}")
print(f"{multiplied_string}")