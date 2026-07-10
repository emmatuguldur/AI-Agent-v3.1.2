#!/usr/bin/env python3
"""
Add the enhanced _pf_run function and other helper functions to ATTACK_TEMPLATE.
This script properly inserts code into the template string.
"""
import json
import re

nb_path = r'c:\Users\Emma\Documents\AI agent v3\AI-Agent-v3.1.2\ai-agent-v3-1-2-single-post-exfiltration.ipynb'

# Read notebook
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find ATTACK_TEMPLATE cell (cell 3, index 3)
template_cell = nb['cells'][3]
current_source = ''.join(template_cell['source'])

print(f"Current template cell source length: {len(current_source)}")
print(f"Last 300 chars:\n{current_source[-300:]}")

# The template is a Python string literal. We need to insert code before the closing quote.
# Find where the template ends: look for the pattern that ends the string
# The string is:  ATTACK_TEMPLATE = 'content\nBANDIT_ENABLE     = __BANDIT_ENABLE__\n'

template_start_pattern = "ATTACK_TEMPLATE = '"
template_start = current_source.find(template_start_pattern)
template_str_start = template_start + len(template_start_pattern)

# The end is at the last single quote (just before the closing paren if any)
# Find all single quotes and take the last one that's on its own line
lines = current_source.split('\n')
last_line = lines[-1] if lines else ""
print(f"\nLast line: {repr(last_line)}")

# The template ends with: ...BANDIT_ENABLE__\n'
# We need to insert new code BEFORE this closing quote

# Reconstruct the position
# Find the position where \\nBandit_ENABLE ends
template_end_marker = "BANDIT_ENABLE     = __BANDIT_ENABLE__\\n'"
if template_end_marker in current_source:
    template_end = current_source.find(template_end_marker) + len(template_end_marker) - 2  # -2 to position before the '
    print(f"\nFound template end marker at position {template_end}")
    print(f"Context around end: ...{current_source[template_end-100:template_end+50]}")
else:
    # Maybe it's not escaped in the file, check directly
    idx = current_source.rfind("BANDIT_ENABLE")
    if idx > 0:
        # Find the closing quote after this
        rest = current_source[idx:]
        quote_idx = rest.find("'")
        if quote_idx > 0:
            template_end = idx + quote_idx
            print(f"\nFound approx template end at {template_end}")
            print(f"Context: {current_source[template_end-50:template_end+50]}")
