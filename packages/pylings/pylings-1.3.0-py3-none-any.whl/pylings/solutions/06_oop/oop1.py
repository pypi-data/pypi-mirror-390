"""
OOP Exercise 1 (oop1.py)
This exercise introduces basic Object-Oriented Programming (OOP) concepts in Python: 
defining classes, initializing attributes, and creating methods.
Follow the TODO instructions and complete each section to pass all tests.
"""

# Define the Car class below
class Car:
    def __init__(self, brand):
        # Initialize the brand attribute with the provided brand
        self.brand = brand
        # Initialize the speed attribute to 0
        self.speed = 0

    def accelerate(self, amount):
        # Increase the car's speed by the given amount
        self.speed += amount

    def brake(self, amount):
        # Decrease the car's speed by the given amount
        # Ensure the speed does not go below 0
        self.speed = max(0, self.speed - amount)

# DO NOT TOUCH 
car = Car("Toyota")
assert car.brand == f"Toyota", "Brand should be set during initialization, got {car.brand}"
assert car.speed == 0, f"Initial speed should be 0, got {car.speed}"

car.accelerate(30)
assert car.speed == 30, f"Speed should be 30 after accelerating by 30, got {car.speed}"

car.brake(10)
assert car.speed == 20, f"Speed should be 20 after braking by 10, got {car.speed}"

car.brake(25)
assert car.speed == 0, f"Speed should never go below 0, got {car.speed}"

print(f"Car:\n\tBrand: {car.brand}\n\tSpeed: {car.speed}")