"""
Compare Format Product Info node between two files.
This is the KEY node that creates session.extra.product_information
from the API data.
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

for label, path in [
    ("VHN_fixing.json", r'C:\Users\Administrator\Desktop\Hoc_python\VHN_fixing.json'),
    ("VHN_DauTien_Fixed.json", r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json'),
]:
    data = load_json(path)
    nodes = find_all_nodes(data.get('sequence', []))
    
    print(f"\n{'='*80}")
    print(f"  {label} - Format Product Info node")
    print(f"{'='*80}")
    
    for node in nodes:
        if node.get('type') == 'python':
            varname = node.get('properties', {}).get('varName', '')
            if varname == 'session.extra.product_information':
                print(f"\n  Node name: {node.get('name')}")
                print(f"  varName: {varname}")
                print(f"\n  FULL expression:")
                print("  " + "-" * 70)
                print(node['properties']['expression'])
                print("  " + "-" * 70)
