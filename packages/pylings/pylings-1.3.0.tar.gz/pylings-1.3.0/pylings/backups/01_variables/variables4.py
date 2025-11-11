"""
Variables Exercise 4 (variables4.py)
This exercise focuses on arithmetic operations, variable correction, and visualizing data using string multiplication.
Follow the TODO instructions and fix any issues.
Uncomment and complete each section to pass all tests.
"""

# === VARIABLE ASSIGNMENT AND ARITHMETIC ===
# TODO: Assign correct values to revenue and cost, then calculate profit.

# TODO: Assign a positive integer value
revenue = __  

# TODO: Assign a non-negative integer value
cost = __

# TODO: Calculate profit (revenue - cost)
profit = __ 

# === STRING MULTIPLICATION FOR VISUALIZATION ===
# TODO: Create a visual representation of cost and profit using '#' characters.

# TODO: Scale cost proportionally using '#' * (cost / revenue) * 25
cost_bar = __ 

# TODO: Scale profit proportionally using '#' * (profit / revenue) * 25
profit_bar = __

# === TESTS ===
# Call the variables to test calculations

assert isinstance(revenue, int) and revenue > 0, f"[FAIL] Revenue must be a positive integer, got '{revenue}'"
assert isinstance(cost, int) and cost >= 0, f"[FAIL] Cost must be a non-negative integer, got '{cost}'"
assert profit == revenue - cost, f"[FAIL] Expected profit '{revenue - cost}', got '{profit}'"
assert isinstance(cost_bar, str) and isinstance(profit_bar, str), f"[FAIL] Expected cost_bar and profit_bar to be strings"

# Validate the length of the hash bars using proportional scaling
expected_cost_length = int((cost / revenue) * 25)
expected_profit_length = int((profit / revenue) * 25)

assert len(cost_bar) == expected_cost_length, f"[FAIL] Expected cost_bar length '{expected_cost_length}', got '{len(cost_bar)}'"
assert len(profit_bar) == expected_profit_length, f"[FAIL] Expected profit_bar length '{expected_profit_length}', got '{len(profit_bar)}'"

# === PRINT RESULTS ===
print('Business revenue:', revenue)
print('Business costs:', cost)
print('The business profit is:', profit)
print('  cost: ' + cost_bar)
print('profit: ' + profit_bar)