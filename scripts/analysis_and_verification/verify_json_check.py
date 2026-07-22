"""
Verify: Does the Python json_check node in VHN_DauTien_Fixed.json
properly clean bot_json_query BEFORE setVar runs?

In VHN_fixing.json, json_check strips markdown and validates JSON.
But does the FIXED file's json_check also strip markdown?
And does it write back to bot_json_query so setVar gets clean JSON?
"""
import json

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_all_nodes(seq, path="root"):
    results = []
    for i, node in enumerate(seq):
        node_path = f"{path}[{i}]"
        results.append((node_path, node))
        if 'sequence' in node:
            results.extend(find_all_nodes(node['sequence'], f"{node_path}.seq"))
        if 'branches' in node:
            for bname, bseq in node['branches'].items():
                results.extend(find_all_nodes(bseq, f"{node_path}.branch[{bname}]"))
    return results

# Compare json_check Python nodes
for label, path in [
    ("VHN_fixing.json", r'C:\Users\Administrator\Desktop\Hoc_python\VHN_fixing.json'),
    ("VHN_DauTien_Fixed.json", r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json'),
]:
    data = load_json(path)
    all_nodes = find_all_nodes(data.get('sequence', []))
    
    print(f"\n{'='*80}")
    print(f"  {label}")
    print(f"{'='*80}")
    
    for fpath, node in all_nodes:
        if node.get('type') == 'python' and 'json_check' in node.get('properties', {}).get('varName', ''):
            print(f"  Path: {fpath}")
            print(f"  varName: {node['properties']['varName']}")
            print(f"\n  FULL expression:")
            print(f"  ---")
            print(node['properties']['expression'])
            print(f"  ---")
            print()

    # Also check B2B path json_check equivalent
    for fpath, node in all_nodes:
        if node.get('type') == 'python' and node.get('properties', {}).get('varName', '') not in ('json_check', ''):
            expr = node.get('properties', {}).get('expression', '')
            if 'ai_query_data' in expr or ('json' in expr.lower() and 'b2b' in fpath.lower()):
                print(f"  [B2B Python node]")
                print(f"  Path: {fpath}")
                print(f"  varName: {node['properties']['varName']}")
                print(f"  expression: {expr[:500]}")
                print()
