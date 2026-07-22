"""
Verify all Python nodes that output session.extra.product_information 
or session.extra.product_wishlist in VHN_DauTien_Fixed.json
"""
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
                results.extend(find_all_nodes(bseq, f"{node_path}.br[{bname}]"))
    return results

fixed = load_json(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json')
all_nodes = find_all_nodes(fixed.get('sequence', []))

print("All Python nodes outputting product data:")
print("=" * 80)

for path, node in all_nodes:
    if node.get('type') == 'python':
        varname = node.get('properties', {}).get('varName', '')
        if 'product' in varname.lower():
            print(f"\nPath: {path}")
            print(f"Name: {node.get('name')}")
            print(f"varName: {varname}")
            expr = node['properties'].get('expression', '')
            # Check if it uses Handlebars syntax or raw Python
            uses_handlebars = '{{' in expr
            print(f"Uses Handlebars {{{{ }}}}: {uses_handlebars}")
            print(f"Expression:")
            print(expr)
            print("-" * 40)
