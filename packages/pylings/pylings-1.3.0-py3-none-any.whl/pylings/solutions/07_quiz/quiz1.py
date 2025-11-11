"""
OOP Quiz (oop_quiz1.py)
This quiz tests your ability to combine variables, data structures, loops, conditionals, and object-oriented programming.
You will create a simple Library system that manages books with multiple attributes.
Follow the TODO instructions and complete each section to pass all tests.
"""

# Define the Book class
class Book:
    def __init__(self, title, author, genre, year):
        # Initialize book attributes: title, author, genre, year
        self.title = title
        self.author = author
        self.genre = genre
        self.year = year
        # Set availability to True by default
        self.available = True

    def borrow(self):
        # Set availability to False if the book is available
        if self.available:
            self.available = False
            return True
        return False

    def return_book(self):
        # Set availability back to True
        if not self.available:
            self.available = True
            return True
        return False

    def __str__(self):
        # Return a string showing book details and availability
        status = "Available" if self.available else "Unavailable"
        return f"{self.title} by {self.author} ({self.genre}, {self.year}) - {status}"


# Define the Library class
class Library:
    def __init__(self):
        # Initialize an empty list to store books
        self.books = []

    def add_book(self, book):
        # Add a book to the library's book list
        self.books.append(book)

    def borrow_book(self, title):
        # Loop through books and borrow the one that matches the title
        for book in self.books:
            if book.title == title:
                return book.borrow()
        return False  # If book not found

    def return_book(self, title):
        # Loop through books and return the one that matches the title
        for book in self.books:
            if book.title == title:
                return book.return_book()
        return False  # If book not found

    def display_books(self):
        # Loop through books and print their status using the __str__ method
        for book in self.books:
            print(book)


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