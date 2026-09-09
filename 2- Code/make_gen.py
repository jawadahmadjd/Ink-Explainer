import json, os

# Create generator script
script_content = '''
import json

# Define the shots data generator
# Each shot has:
# - text: Spoken VO text
# - visual: Visual scene description
# - prompt: Exact prompt for Google Nano Banana Pro
'''
with open("generate_storyboard.py", "w", encoding="utf-8") as f:
    f.write(script_content)
print("Base generator created.")
