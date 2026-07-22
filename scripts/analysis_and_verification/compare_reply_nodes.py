"""
Compare the B2C reply node's instruction to find why hallucination occurs.
Focus on: Does it reference session.extra.product_information correctly?
Does it have HARD RULES against hallucination like VHN_fixing does?
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

# Get full instruction for both reply nodes
for label, path in [
    ("VHN_fixing.json", r'C:\Users\Administrator\Desktop\Hoc_python\VHN_fixing.json'),
    ("VHN_DauTien_Fixed.json", r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json'),
]:
    data = load_json(path)
    nodes = find_all_nodes(data.get('sequence', []))
    
    print(f"\n{'='*80}")
    print(f"  {label}")
    print(f"{'='*80}")
    
    for node in nodes:
        name = node.get('name', '')
        if node.get('type') == 'qna' and ('B2C' in name or 'Recommend Product' in name or 'Gather Requirement' in name):
            inst = node.get('properties', {}).get('instruction', '')
            knowledge = node.get('properties', {}).get('knowledge', '')
            print(f"\n  Node: {name}")
            print(f"  varReply: {node.get('properties', {}).get('varReply')}")
            print(f"  knowledge: {knowledge}")
            
            # Check for product_information references
            if 'product_information' in inst:
                print(f"  HAS product_information reference: YES")
                # Extract the relevant section
                idx = inst.find('product_information')
                start = max(0, idx - 200)
                end = min(len(inst), idx + 200)
                print(f"  Context around 'product_information':")
                print(f"  ...{inst[start:end]}...")
            elif 'findproduct_data' in inst:
                print(f"  HAS findproduct_data reference: YES")
                idx = inst.find('findproduct_data')
                start = max(0, idx - 200)
                end = min(len(inst), idx + 200)
                print(f"  Context around 'findproduct_data':")
                print(f"  ...{inst[start:end]}...")
            else:
                print(f"  HAS product_information reference: NO")
                print(f"  HAS findproduct_data reference: NO")
            
            # Check for anti-hallucination rules
            has_source_of_truth = 'SOURCE OF TRUTH' in inst
            has_no_guessing = 'No guessing' in inst or 'KHÔNG bịa' in inst
            has_hard_rules = 'HARD RULE' in inst
            print(f"  Has 'SOURCE OF TRUTH': {has_source_of_truth}")
            print(f"  Has anti-guessing: {has_no_guessing}")
            print(f"  Has HARD RULES: {has_hard_rules}")
            
            # Check if knowledge field contains product data
            if 'product_information' in knowledge or 'findproduct_data' in knowledge:
                print(f"  Knowledge contains product data: YES")
            else:
                print(f"  Knowledge contains product data: NO")
