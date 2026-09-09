# Build python script that defines the 7 Acts with ~350 shots
code = """
import json, csv

# We will define sequences for each Act.
# Total target: ~350 shots, ~11,200 chars total.
"""
with open("test_builder.py", "w") as f:
    f.write(code)
print("Ready to construct shots.")
