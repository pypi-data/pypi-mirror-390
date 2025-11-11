"""
If Statements Exercise 2 (conditionals2.py)
This exercise introduces if-elif-else blocks in Python.
Follow the TODO instructions and fix any issues.
Uncomment and complete each section to pass all tests.
"""

# === IF-ELIF-ELSE FUNCTION ===
# TODO: Create a function that classifies a number as positive, negative, or zero

def classify_number(number):
    if number __ 0:  # TODO: Replace __ with the correct condition for positive numbers
        return "Positive"
    elif number __ 0:  # TODO: Replace __ with the correct condition for zero
        return "Zero"
    else:
        return "Negative"

# === GRADE CLASSIFICATION FUNCTION ===
# TODO: Create a function that assigns a letter grade based on a score

def assign_grade(score):
    if score __ 90:  # TODO: Score >= 90
        return "A"
    elif score __ 80 :  # TODO: Score >= 80
        return "B"
    elif score __ 70:  # TODO: Score >= 70
        return "C"
    elif score __ 60:  # TODO: Score >= 60
        return "D"
    else:
        return "F"

# === TESTS ===
# Call the functions with various inputs to test all conditions

# Test classify_number
result_one = classify_number(10)
assert result_one == "Positive", f"[FAIL] Expected 'Positive', got '{result_one}'"

result_two = classify_number(0)
assert result_two == "Zero", f"[FAIL] Expected 'Zero', got '{result_two}'"

result_three = classify_number(-5)
assert result_three == "Negative", f"[FAIL] Expected 'Negative', got '{result_three}'"

# Test assign_grade
result_four = assign_grade(95)
assert result_four == "A", f"[FAIL] Expected 'A', got '{result_four}'"

result_five = assign_grade(85)
assert result_five == "B", f"[FAIL] Expected 'B', got '{result_five}'"

result_six = assign_grade(75)
assert result_six == "C", f"[FAIL] Expected 'C', got '{result_six}'"

result_seven = assign_grade(65)
assert result_seven == "D", f"[FAIL] Expected 'D', got '{result_seven}'"

result_eight = assign_grade(50)
assert result_eight == "F", f"[FAIL] Expected 'F', got '{result_eight}'"

print(f"\n{result_one}\n{result_two}\n{result_three}\n{result_four}\n{
    result_five}\n{result_six}\n{result_seven}\n{result_eight}.")