"""
In this exercise, we are going to introduce the concept of tuples.

In Python, a tuple is an immutable collection of items,
which can be of different data types:

- A tuple is an ordered collection of items enclosed in parentheses `()`.

- Tuples cannot be modified after their creation (e.g., adding, removing, or changing elements is not allowed).

- Each item in a tuple has a specific index, starting from 0.

- Tuples can contain items of different data types (e.g., integers, strings, other tuples).


"""

# TODO: Initialize a tuple of programming languages with "Python", "Java", "Rust", and "C++"
languages = ("Python","Java","Rust","C++")


# DO NOT TOUCH
assert languages == ("Python", "Java", "Rust", "C++"), f"Expected ('Python', 'Java', 'Rust', 'C++'), but got {languages}"
print(f"Languages: {languages}")

# TODO: Access the third item in the tuple, remember 0 indexed
second_language = languages[2]

# DO NOT TOUCH
assert second_language == ("Rust"), f"Expected 'Rust', but got {second_language}"
print(f"Second Language: {second_language}")

# TODO: Create a new tuple by adding "JavaScript" to the existing tuple
new_languages = languages + ("JavaScript",)

# DO NOT TOUCH
assert new_languages == ("Python", "Java", "Rust", "C++", "JavaScript"), f"Expected ('Python', 'Java', 'Rust', 'C++', 'JavaScript'), but got {new_languages}"
print(f"New languages: {new_languages}")

# TODO: Create a new tuple by inserting "Ruby" at index 4, 
new_languages_with_ruby = new_languages[:4] + ("Ruby",) + new_languages[4:]

# DO NOT TOUCH
assert new_languages_with_ruby == ("Python", "Java", "Rust", "C++", "Ruby", "JavaScript"), f"Expected ('Python', 'Java', 'Rust', 'C++', 'Ruby', 'JavaScript'), but got {new_languages_with_ruby}"
print(f"New languages with ruby: {new_languages_with_ruby}")

# TODO: Create a new tuple by removing the second item
new_languages_without_second = new_languages[:1] + new_languages[2:]

# DO NOT TOUCH
assert new_languages_without_second == ("Python", "Rust", "C++", "JavaScript"), f"Expected ('Python', 'Rust', 'C++',,'JavaScript'), but got {new_languages_without_second}"
print(f"Remaining languages: {new_languages_without_second}")