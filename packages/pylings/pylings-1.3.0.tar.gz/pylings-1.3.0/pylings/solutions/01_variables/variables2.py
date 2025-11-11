"""
Welcome to the Pylings temperature conversion exercise!
Your goal is to practice working with variables and temperature conversions in Python.



"""

# TODO: Assign the name of the temperature scale in Celsius to the variable 'celsius_name'
celsius_name = "Celsius"

# TODO: Assign the temperature in Celsius 100.10 to the variable 'celsius_temp'
celsius_temp = 100.10

# TODO: Assign the name of the temperature scale in Fahrenheit to the variable 'fahrenheit_name'
fahrenheit_name = "Fahrenheit"

"""
TODO: Convert the temperature from Celsius to Fahrenheit and assign it to 'fahrenheit_temp'

Formula is (celsius multiplied by 9/5) plus 32
"""
fahrenheit_temp = (celsius_temp * 9/5) + 32

# TODO: Assign the name of the temperature scale in Kelvin to the variable 'kelvin_name'
kelvin_name = "Kelvin"

"""
TODO: Convert the temperature from Celsius to Kelvin by incrementing Celsius by 273.15, and assign it to 'kelvin_temp'

Formula is celsius incremented by 273.15

"""
kelvin_temp = celsius_temp + 273.15

# === TESTS ===
# DO NOT TOUCH
assert celsius_name == "Celsius", f"Expected 'Celsius', but got {celsius_name}"
assert celsius_temp == 100.10, f"Expected 100.10, but got {celsius_temp}"
assert fahrenheit_temp == 212.18, f"Expected 212.18, but got {fahrenheit_temp}"
assert fahrenheit_name == "Fahrenheit", f"Expected 'Fahrenheit', but got {fahrenheit_name}"
assert kelvin_name == "Kelvin", f"Expected 'Kelvin', but got {kelvin_name}"
assert kelvin_temp == 373.25, f"Expected 373.25, but got {kelvin_temp}"

# Print the variables to see their values.
print(f"Temperature in {celsius_name}: {celsius_temp}")
print(f"Temperature in {fahrenheit_name}: {fahrenheit_temp}")
print(f"Temperature in {kelvin_name}: {kelvin_temp}")
