"""
OOP Exercise 3 (oop3.py)
This exercise introduces inheritance and method overriding.
You will extend the Car class to create a specialized ElectricCar subclass.
Follow the TODO instructions and complete each section to pass all tests.
"""

# Define the Car class
class Car:
    def __init__(self, brand):
        self.brand = brand
        self.speed = 0

    def accelerate(self, amount):
        self.speed += amount

    def brake(self, amount):
        self.speed = max(0, self.speed - amount)

    def __str__(self):
        return f"{self.brand} traveling at {self.speed} km/h"


# Define the ElectricCar subclass below
class ElectricCar(Car):
    def __init__(self, brand):
        # TODO: Call the parent class constructor using super()
        # TODO: Initialize battery_level to 100
        pass

    def accelerate(self, amount):
        # TODO: Call the parent's accelerate method
        # TODO: Decrease battery_level by 1% per acceleration
        pass
    
    def brake(self, amount):
        # TODO: Decreases the car's speed by the given amount
        # TODO: Call parents break method
        # TODO: Increase battery_level by 1% per brake
        pass

    def __str__(self):
        # Return a string showing "brand travelling at speed km/h with battery level% battery"
        pass

# Tests to check if your class works
e_car = ElectricCar("Tesla")
assert e_car.brand == "Tesla", f"Expected: Telsa, but got {e_car.brand}"
assert e_car.battery_level == 100, f"Expected: 100, but got {e_car.battery_level}"

e_car.accelerate(20)
assert e_car.speed == 20, f"Expected: 20, but got {e_car.speed}"
assert e_car.battery_level == 99, f"Expected: 99, but got {e_car.battery_level}"

e_car.brake(10)
assert e_car.speed == 10, f"Expected, 10, but got {e_car.speed}"

assert str(e_car) == "Tesla traveling at 10 km/h with 100% battery", f"Expected, Tesla traveling at 10 km/h with 100% battery, but got {str(e_car)}"

print(f"Electic car: {str(e_car)}")