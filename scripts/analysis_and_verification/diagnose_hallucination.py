"""
ROOT CAUSE ANALYSIS for hallucination.
 
Two suspected issues:
1. GPT-4 Query Data prompt was changed to force arrays ["christina"] instead of strings "christina".
   When Handlebars renders {{ session.extra.query_data.vendor }} for an array,
   the API might receive malformed value → returns wrong/empty data.
   
2. Format Product Info uses exact match (title == names).
   If AI Analyze returns slightly different name than API data, match FAILS → output empty → hallucination.

Solution:
1. Revert GPT-4 Query Data instruction to VHN_fixing.json's EXACT version
2. Make Format Product Info use robust matching (substring/contains instead of ==)
"""
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_all_nodes(seq):
    results = []
    for node in seq:
        results.append(node)
        if 'sequence' in node:
            results.extend(find_all_nodes(node['sequence']))
        if 'branches' in node:
            for b in node['branches'].values():
                results.extend(find_all_nodes(b))
    return results

# Get the EXACT instruction from VHN_fixing.json
fixing = load_json(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_fixing.json')
fixing_nodes = find_all_nodes(fixing.get('sequence', []))

fixing_instruction = None
for node in fixing_nodes:
    if node.get('id') == '52532d1c2a7a9307df8455e1d70a9c05':  # Same ID in both files
        fixing_instruction = node['properties']['instruction']
        break

# Compare key differences
fixed = load_json(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json')
fixed_nodes = find_all_nodes(fixed.get('sequence', []))

for node in fixed_nodes:
    if node.get('id') == '52532d1c2a7a9307df8455e1d70a9c05':
        fixed_instruction = node['properties']['instruction']
        
        # Check key differences
        if 'phải là array' in fixed_instruction:
            print("PROBLEM FOUND: GPT-4 Query Data prompt forces arrays!")
            print("  VHN_fixing says: 'có thể là 1 giá trị, hoặc là array'")
            print("  VHN_Fixed says: 'phải là array'")
            print("  This causes vendor to be ['christina'] instead of 'christina'")
            print("  Handlebars may render this incorrectly in API body")
        
        if '["none"]' in fixed_instruction:
            print("\nPROBLEM FOUND: Default values changed to arrays!")
            print("  VHN_fixing: 'Giá trị mặc định ban đầu của \"vendor\" là \"none\"'")
            print("  VHN_Fixed: 'Giá trị mặc định ban đầu của \"vendor\" là [\"none\"]'")

print("\n\nFIXING_INSTRUCTION available:", fixing_instruction is not None)
print("Length:", len(fixing_instruction) if fixing_instruction else 0)
