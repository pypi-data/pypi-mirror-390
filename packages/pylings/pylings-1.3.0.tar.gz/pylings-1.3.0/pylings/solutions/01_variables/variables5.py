"""
Variables Exercise 5 (variables5.py)
This exercise focuses on string indexing and slicing using a DNA sequence.
Follow the TODO instructions and fix any issues.
Uncomment and complete each section to pass all tests.

In DNA each letter is defined as a `base`, we can interchange `base` with `index`
"""

# === DNA STRING INDEXING ===
# Solution: Extract specific characters from the DNA sequence

dna_sequence = "AGCTTAGGCTA"
first_base = dna_sequence[0]  # Extract the first base of dna_sequence
last_base = dna_sequence[-1]  # Extract the last base of dna_sequence
third_base = dna_sequence[2]  # Extract the third base of dna_sequence

# === DNA STRING SLICING ===
# Solution: Extract substrings using slicing

first_five_bases = dna_sequence[:5]  # Extract the first five bases of dna_sequence
last_five_bases = dna_sequence[-5:]  # Extract the last five bases of dna_sequence
middle_bases = dna_sequence[4:8]  # Extract the middle four bases (assuming dna_sequence has 10+ bases)

# === DNA REVERSE COMPLEMENT (BASIC) ===
# Solution: Reverse the DNA sequence using slicing

reversed_dna = dna_sequence[::-1]  # Reverse dna_sequence using slicing

# === TESTS ===
# Call the variables to test DNA string indexing and slicing

assert first_base == "A", f"[FAIL] Expected 'A', got '{first_base}'"
assert last_base == "A", f"[FAIL] Expected 'A', got '{last_base}'"
assert third_base == "C", f"[FAIL] Expected 'C', got '{third_base}'"
assert first_five_bases == "AGCTT", f"[FAIL] Expected 'AGCTT', got '{first_five_bases}'"
assert last_five_bases == "GGCTA", f"[FAIL] Expected 'GGCTA', got '{last_five_bases}'"
assert middle_bases == "TAGG", f"[FAIL] Expected 'TAGG', got '{middle_bases}'"
assert reversed_dna == "ATCGGATTCGA", f"[FAIL] Expected 'ATCGGATTCGA', got '{reversed_dna}'"

print(f"DNA Sequence: {dna_sequence}")
print(f"First base:{first_base}")
print(f"Third base:{third_base}")
print(f"Last base:{last_base}")

print(f"First Five base:{first_five_bases}")
print(f"Middle base:{middle_bases}")
print(f"Last Five base:{last_five_bases}")

print(f"DNA Sequence Reversed: {reversed_dna}")