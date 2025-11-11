"""
OOP Quiz (oop_quiz1.py)
This quiz tests your ability to combine variables, data structures, loops, conditionals, and object-oriented programming.
You will create a simple Library system that manages books with multiple attributes.
Follow the TODO instructions and complete each section to pass all tests.
"""

"""TODO: Define the Book class

Define the __init__ method
    - Initialize attributes: title, author, genre, year, and availability (set to True by default)
 
Define the borrow() method
    - Check if the book is available
    - If available, set it to unavailable and return True
    - If not available, return False

Define the return_book() method
    - Set the book's availability back to True
    - Return True if the book was successfully returned, otherwise False

Define the __str__ method
    - Return a string with book details and availability status
    - Format: "Title by Author (Genre, Year) - Available/Unavailable"
"""

"""
TODO: Define the Library class

Define the __init__ method
    - Initialize an empty list to store books

Define the add_book() method
    - Add a book object to the list of books

Define the borrow_book() method
    - Loop through books and find the book that matches the given title
    - If found, attempt to borrow the book and return the result (True or False)

Define the return_book() method
    - Loop through books and find the book that matches the given title
    - Attempt to return the book and return the result (True or False)

Define the display_books() method
    - Loop through all books and print their status using their __str__ method
"""

# Tests to check if your code works
library = Library()
book1 = Book("1984", "George Orwell", "Dystopian", 1949)
book2 = Book("Brave New World", "Aldous Huxley", "Science Fiction", 1932)
book3 = Book("Fahrenheit 451", "Ray Bradbury", "Dystopian", 1953)

library.add_book(book1)
library.add_book(book2)
library.add_book(book3)

# Borrow and return actions
assert library.borrow_book("1984") == True, "Should be able to borrow '1984'"
assert library.borrow_book("1984") == False, "'1984' should not be available for borrowing again"
assert library.return_book("1984") == True, "Should be able to return '1984'"
assert library.borrow_book("1984") == True, "Should be able to borrow '1984' after returning"

# Display books
library.display_books()