"""
Variables Exercise 4 (variables4.py)
This exercise focuses on arithmetic operations, variable correction, and visualizing data using string multiplication.
Follow the TODO instructions and fix any issues.
Uncomment and complete each section to pass all tests.
"""

# === VARIABLE ASSIGNMENT AND ARITHMETIC ===
# Solution: Assign correct values to revenue and cost, then calculate profit.

revenue = 10000  # Assign a positive integer value
cost = 6000  # Assign a non-negative integer value
profit = revenue - cost  # Calculate profit (revenue - cost)

# === STRING MULTIPLICATION FOR VISUALIZATION ===
# Solution: Create a visual representation of cost and profit using '#' characters.

cost_bar = '#' * int((cost / revenue) * 25)  # Scale cost proportionally
profit_bar = '#' * int((profit / revenue) * 25)  # Scale profit proportionally

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
