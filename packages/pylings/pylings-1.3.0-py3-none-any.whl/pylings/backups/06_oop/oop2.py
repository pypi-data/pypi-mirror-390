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
        pass

    def accelerate(self, amount):
        # Increases the car's speed by the given amount
        self.speed += amount

    def brake(self, amount):
        # Decreases the car's speed by the given amount
        # Ensures the speed does not go below 0
        self.speed = max(0, self.speed - amount)

    def __str__(self):
        # TODO: Return a the string in following format, "Toyota travelling at 20 km/h"
        pass

    def __repr__(self):
        # TODO: Return a technical string that shows how to recreate the object
        pass

# Tests to check if your class works
car = Car("Ford")
assert str(car) == "Ford traveling at 0 km/h", f"Should get, Ford traveling at 0 km/h, but got {str(car)}"

car.accelerate(50)
assert str(car) == "Ford traveling at 50 km/h", f"Should get, Ford traveling at 50 km/h, but got {str(car)}"
assert repr(car) == "Car('Ford', 50)", f"Should return a recreatable object representation, Car('Ford', 50), but got {repr(car)}"

print(f"Car:\n\t{car.brand}\n\t{car.speed}")
