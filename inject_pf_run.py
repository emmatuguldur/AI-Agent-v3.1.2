#!/usr/bin/env python3
"""
Insert the enhanced _pf_run function with Thompson Sampling/UCB into the ATTACK_TEMPLATE.
"""
import json
import re

# Read notebook
nb_path = r'c:\Users\Emma\Documents\AI agent v3\AI-Agent-v3.1.2\ai-agent-v3-1-2-single-post-exfiltration.ipynb'
with open(nb_path) as f:
    nb = json.load(f)

# Find the ATTACK_TEMPLATE cell (cell 3, index 3)
template_cell = nb['cells'][3]
assert 'ATTACK_TEMPLATE' in ''.join(template_cell['source']), "Wrong cell"

# Get current source
current_source = ''.join(template_cell['source'])

# Find the template string content
# It starts with "ATTACK_TEMPLATE = '" and ends with "')"
template_start = current_source.find("ATTACK_TEMPLATE = '") + len("ATTACK_TEMPLATE = '")
template_end = current_source.rfind("'")

template_str = current_source[template_start:template_end]

# The template string has \n literals we need to handle
# Convert to actual code by processing escape sequences
template_code = template_str.encode().decode('unicode_escape')

print("=" * 80)
print("Current template code (last 1000 chars):")
print("=" * 80)
print(template_code[-1000:])
print("=" * 80)

# Find where to insert the _pf_run function
# Look for the line: "def _pf_run(env, budget, max_hops):"
pf_run_marker = "def _pf_run(env, budget, max_hops):"
if pf_run_marker in template_code:
    print(f"\nFound existing _pf_run function - need to REPLACE it")
    # Find the start and end of this function
    func_start = template_code.find(pf_run_marker)
    print(f"Function starts at: {func_start}")
    
    # Find the next "def " or "class " after this one to know where it ends
    remaining = template_code[func_start + len(pf_run_marker):]
    next_def = remaining.find("\ndef ")
    if next_def < 0:
        next_def = remaining.find("\nclass ")
    
    if next_def > 0:
        func_end = func_start + len(pf_run_marker) + next_def
        print(f"Function ends at: {func_end}")
        print(f"\nOld function (first 500 chars):")
        print(template_code[func_start:func_start+500])
    else:
        print("Could not find function end!")
else:
    print(f"\nDid NOT find existing _pf_run function - this is unexpected!")
    print(f"Looking for: {pf_run_marker}")
