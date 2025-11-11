"""
Variables Exercise 3 (variables3.py)
This exercise focuses on string concatenation, different ways to combine variables, and string multiplication.
Follow the TODO instructions and fix any issues.
Uncomment and complete each section to pass all tests.
"""

# === BASIC STRING CONCATENATION ===
# TODO: Combine first_name and last_name into full_name using concatenation

first_name = "John"
last_name = "Cleese"

# TODO: Concatenate first_name and last_name with a space in between
full_name = __ 

# === CONCATENATION WITH NUMBERS ===
# TODO: Convert number to string and concatenate with a message

age = 50

# TODO: Concatenate "I am " + age + " years old." (age must be converted to a string)
message = __

# === CONCATENATION USING F-STRINGS ===
# TODO: Use an f-string to format a message with name and age

# TODO: Use f"{full_name} is {age} years old."
f_string_message = __

# === CONCATENATION USING .FORMAT() ===
# TODO: Use .format() method to create a message

# TODO: Use "{} is {} years old.".format(full_name, age)
format_message = __  

# === STRING MULTIPLICATION ===
# TODO: Repeat a string multiple times using the * operator

repeat_word = "Hello"

# TODO: Repeat "Hello" 3 times (output: "HelloHelloHello")
multiplied_string = __ 

# === TESTS ===
# Call the variables to test concatenation methods

assert full_name == "John Cleese", f"[FAIL] Expected 'John Cleese', got '{full_name}'"
assert message == "I am 50 years old.", f"[FAIL] Expected 'I am 50 years old.', got '{message}'"
assert f_string_message == "John Cleese is 50 years old.", f"[FAIL] Expected 'John Cleese is 50 years old.', got '{f_string_message}'"
assert format_message == "John Cleese is 50 years old.", f"[FAIL] Expected 'John Cleese is 50 years old.', got '{format_message}'"
assert multiplied_string*3 == "HelloHelloHelloHelloHelloHelloHelloHelloHello", f"[FAIL] Expected 'HelloHelloHelloHelloHelloHelloHelloHelloHello', got '{multiplied_string}'"

print(f"{full_name}")
print(f"{message}")
print(f"{f_string_message}")
print(f"{multiplied_string}")