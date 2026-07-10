import json
import re

# Read notebook
with open(r'c:\Users\Emma\Documents\AI agent v3\AI-Agent-v3.1.2\ai-agent-v3-1-2-single-post-exfiltration.ipynb') as f:
    nb = json.load(f)

# Find the ATTACK_TEMPLATE cell
template_cell = None
template_cell_idx = None
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if 'ATTACK_TEMPLATE = ' in source:
            template_cell = cell
            template_cell_idx = i
            break

if template_cell is None:
    print("ERROR: Could not find ATTACK_TEMPLATE cell")
    exit(1)

# Get the current template content
source = ''.join(template_cell.get('source', []))

# Find where the template string ends (the last single quote before .replace)
# The template is inside a multi-line string that starts with ATTACK_TEMPLATE = '

# Extract the part after ATTACK_TEMPLATE = '
start_marker = "ATTACK_TEMPLATE = '"
start_idx = source.find(start_marker)
if start_idx < 0:
    print("ERROR: Could not find ATTACK_TEMPLATE = ' marker")
    exit(1)

# Find the closing quote - it's tricky because the string has \n in it
# Look for the pattern:  ... }\n\'
# Actually, let's look for the last .replace call before we create the file

# First, let's just verify we can see the end
print(f"Template cell found at index {template_cell_idx}")
print(f"Source length: {len(source)} chars")
print(f"Last 200 chars of source:\n{source[-200:]}")
print("\nFirst 300 chars of source:")
print(source[:300])
