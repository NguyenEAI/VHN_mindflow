import json

with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    fixing_data = json.load(f)

# Extract correct properties from VHN_fixing.json
nodes_to_copy = {}
def extract_fixing(seq):
    for node in seq:
        if node.get('id') == '52532d1c2a7a9307df8455e1d70a9c05': # GPT-4 Query Data
            nodes_to_copy['query_data'] = node['properties']
        elif node.get('id') == 'fb5a13c13db9c1499f374e20e623e775': # API CALL in fixing
            nodes_to_copy['api_call'] = node['properties']
        elif node.get('id') == '6d3f02d97dab85e491a60d076f675a58': # GPT-4 Analysis
            nodes_to_copy['analysis'] = node['properties']
        
        if 'sequence' in node: extract_fixing(node['sequence'])
        if 'branches' in node:
            for b in node['branches'].values(): extract_fixing(b)

extract_fixing(fixing_data.get('sequence', []))

with open('VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    fixed_data = json.load(f)

def apply_patch(seq):
    changed = False
    for node in seq:
        # Patch GPT-4 Query Data
        if node.get('id') == '52532d1c2a7a9307df8455e1d70a9c05' and 'query_data' in nodes_to_copy:
            node['properties'] = nodes_to_copy['query_data']
            changed = True
            print("Patched GPT-4 Query Data (B2C)")
            
        # Patch BOTH API CALL PRODUCT DATA nodes in B2C
        elif node.get('id') in ['3173e7d6fcbdeb4100c4dfabad2c1bbd', 'fb5a13c13db9c1499f374e20e623e775']:
            if 'api_call' in nodes_to_copy:
                node['properties'] = nodes_to_copy['api_call']
                changed = True
                print(f"Patched API CALL PRODUCT DATA ({node.get('id')})")
                
        # Patch GPT-4 Analysis
        elif node.get('id') == '6d3f02d97dab85e491a60d076f675a58' and 'analysis' in nodes_to_copy:
            node['properties'] = nodes_to_copy['analysis']
            changed = True
            print("Patched GPT-4 Analysis (B2C)")
            
        if 'sequence' in node:
            if apply_patch(node['sequence']): changed = True
        if 'branches' in node:
            for b in node['branches'].values():
                if apply_patch(b): changed = True
    return changed

if apply_patch(fixed_data.get('sequence', [])):
    with open('VHN_DauTien_Fixed.json', 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)
    print("ALL PATCHED SUCCESSFULLY")
else:
    print("NO CHANGES MADE")
