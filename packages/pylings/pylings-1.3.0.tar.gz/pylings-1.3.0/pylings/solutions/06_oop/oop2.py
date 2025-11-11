"""
OOP Exercise 2 (oop2.py)
This exercise introduces Python's special methods: __str__ and __repr__.
These methods control how instances of your class are represented as strings.
Follow the TODO instructions and complete each section to pass all tests.
"""

# Define the Car class below
class Car:
    def __init__(self, brand):
        # Initializes the brand attribute with the provided brand
        self.brand = brand
        # Initializes the speed attribute to 0
        self.speed = 0

    def accelerate(self, amount):
        # Increases the car's speed by the given amount
        self.speed += amount

    def brake(self, amount):
        # Decreases the car's speed by the given amount, ensuring it doesn't go below 0
        self.speed = max(0, self.speed - amount)

    def __str__(self):
        # Returns a user-friendly string describing the car's status
        return f"{self.brand} traveling at {self.speed} km/h"

    def __repr__(self):
        # Returns a technical string that shows how to recreate the object
        return f"Car('{self.brand}', {self.speed})"


# Tests to check if your class works
car = Car("Ford")
assert str(car) == "Ford traveling at 0 km/h", "Initial string representation should show speed 0"

car.accelerate(50)
assert str(car) == "Ford traveling at 50 km/h", "After accelerating, string should reflect new speed"
assert repr(car) == "Car('Ford', 50)", "repr should return a recreatable object representation"

car.brake(60)
assert str(car) == "Ford traveling at 0 km/h", "Speed should not go below 0 after braking"

print("All tests passed!")
