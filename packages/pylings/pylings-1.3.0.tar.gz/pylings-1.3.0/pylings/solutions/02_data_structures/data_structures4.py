"""
In this exercise, we are going to introduce the concept of sets through a scenario: managing unique items in a collection.

In Python, a set is an unordered collection of unique items:

- Sets are defined using curly braces `{}` or the built-in `set()` function.
- Sets do not allow duplicate values.
- Sets are unordered, meaning there is no indexing or ordering of elements.
- Sets support various operations like union, intersection, difference, and more.

"""

# TODO: Initialize a list of items with some duplicates
item_list = ["item1", "item2", "item3", "item1", "item4", "item2", "item5"]

# TODO: Convert the list to a set to remove duplicates
unique_items = set(item_list)

# DO NOT TOUCH
assert unique_items == {"item1", "item2", "item3", "item4", "item5"}, f"Expected unique item set, but got {unique_items}"
print(f"Unique items: {unique_items}")

# TODO: Add a new item "item6" to the set
unique_items.add("item6")

# DO NOT TOUCH
assert "item6" in unique_items, f"Expected 'item6' to be in the set, but got {unique_items}"
print(f"Items after adding 'item6': {unique_items}")

# TODO: Remove the item "item4" from the set
unique_items.remove("item4")

# DO NOT TOUCH
assert "item4" not in unique_items, f"Expected 'item4' to be removed, but got {unique_items}"
print(f"Items after removing 'item4': {unique_items}")

# TODO: Find the difference between `unique_items` and a set of {"item2", "item5"}
remaining_items = unique_items.difference({"item2", "item5"})

# DO NOT TOUCH
assert remaining_items == {"item1", "item3", "item6"}, f"Expected {{'item1', 'item3', 'item6'}}, but got {remaining_items}"
print(f"Items after difference operation: {remaining_items}")