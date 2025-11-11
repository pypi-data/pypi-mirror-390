"""
In this exercise we are going to introduce the concept of lists. 

In Python, a list is a versatile and mutable collection of items,
which can be of different data types:

- A list is an ordered collection of items enclosed in square brackets `[]`.

- Lists can be modified after their creation (e.g., adding, removing, or changing elements).

- Each item in a list has a specific index, starting from 0.

- Lists can contain items of different data types (e.g., integers, strings, other lists).
"""

# TODO: Initialize a list of fruits with "apple", "banana" and "cherry"
fruits = []

# DO NOT TOUCH
assert fruits == ["apple", "banana", "cherry"], f"Expected ['apple', 'banana', 'cherry'], but got {fruits}"

# TODO: Append a "pineapple" to the list

fruits.append()

# DO NOT TOUCH
assert fruits == ["apple", "banana", "cherry", "pineapple"], f"Expected ['apple', 'banana', 'cherry', 'pineapple'], but got {fruits}"

# TODO: Insert "elderflower" into index 3 of fruits
fruits.insert()

# DO NOT TOUCH
assert fruits == ["apple", "banana", "cherry", "elderflower", "pineapple"], f"Expected ['apple', 'elderberry', 'banana', 'cherry', 'date'], but got {fruits}"

# TODO: Pop the second index from fruitslist
popped_fruit = fruits.pop()

# DO NOT TOUCH
assert popped_fruit == "banana", f"Expected 'banana', but got {popped_fruit}"
assert fruits == ["apple", "cherry", "elderflower", "pineapple"], f"Expected ['apple', 'cherry','elderberry', 'pineapple'], but got {fruits}"

# TODO: Remove a fruit "elderflower"
fruits.remove()

assert fruits == ["apple", "cherry", "pineapple"], f"Expected ['apple', 'cherry', 'pineapple'], but got {fruits}"

print(f"Remaining fruits: {fruits}")