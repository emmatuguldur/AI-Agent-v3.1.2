import json
import codecs

f = json.load(open(r'c:\Users\Emma\Documents\AI agent v3\AI-Agent-v3.1.2\ai-agent-v3-1-2-single-post-exfiltration.ipynb'))
cell = [c for c in f['cells'] if c['cell_type']=='code' and any('ATTACK_TEMPLATE =' in line for line in c.get('source',[]))][0]
code = ''.join(cell['source'])

# Extract the part after ATTACK_TEMPLATE = '
start = code.find("ATTACK_TEMPLATE = '") + len("ATTACK_TEMPLATE = '")
end = code.rfind("'")
template = code[start:end]

# Unescape the template
template = codecs.decode(template, 'unicode_escape')

# Find _pf_run function
pf_start = template.find('def _pf_run(')
if pf_start > 0:
    # Print the full function (approximately)
    section = template[pf_start:pf_start+5000]
    print(section)
