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

# Find portfolio mode implementation
portfolio_start = template.find('if MODE == "portfolio":')
if portfolio_start > 0:
    # Print a good chunk from that point
    section = template[portfolio_start:portfolio_start+4000]
    print(section)
    print("\n\n=== CONTINUING ===\n\n")
    print(template[portfolio_start+4000:portfolio_start+8000])
