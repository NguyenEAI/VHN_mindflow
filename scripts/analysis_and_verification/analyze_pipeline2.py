"""
Deep analysis: Compare FULL product retrieval pipeline.
Fixed encoding issue.
"""
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_all_nodes_with_path(seq, path="root"):
    results = []
    for i, node in enumerate(seq):
        node_path = f"{path}[{i}]"
        results.append((node_path, node))
        if 'sequence' in node:
            results.extend(find_all_nodes_with_path(node['sequence'], f"{node_path}.seq"))
        if 'branches' in node:
            for bname, bseq in node['branches'].items():
                results.extend(find_all_nodes_with_path(bseq, f"{node_path}.br[{bname}]"))
    return results

def safe_print(s):
    try:
        print(s)
    except:
        print(s.encode('ascii', errors='replace').decode('ascii'))

def dump_node_details(node, indent="    "):
    t = node.get('type')
    safe_print(f"{indent}type={t}, name={node.get('name')}, id={node.get('id')}")
    if t == 'qna':
        safe_print(f"{indent}  varReply={node.get('properties', {}).get('varReply')}")
        inst = node.get('properties', {}).get('instruction', '')
        safe_print(f"{indent}  knowledge={node.get('properties', {}).get('knowledge', '')}")
        safe_print(f"{indent}  instruction (first 800 chars):")
        safe_print(f"{indent}  {inst[:800]}")
    elif t == 'python':
        safe_print(f"{indent}  varName={node.get('properties', {}).get('varName')}")
        expr = node.get('properties', {}).get('expression', '')
        safe_print(f"{indent}  expression:")
        safe_print(f"{indent}  {expr[:1000]}")
    elif t == 'setVar':
        safe_print(f"{indent}  varName={node.get('properties', {}).get('varName')}")
        safe_print(f"{indent}  varValue={node.get('properties', {}).get('varValue')}")
    elif t == 'botAPICall':
        safe_print(f"{indent}  api_url={node.get('properties', {}).get('api_url')}")
        safe_print(f"{indent}  api_body={node.get('properties', {}).get('api_body')}")
        safe_print(f"{indent}  api_response_var_name={node.get('properties', {}).get('api_response_var_name')}")
    elif t == 'if':
        safe_print(f"{indent}  condition={node.get('properties', {}).get('condition')}")
    elif t == 'block':
        safe_print(f"{indent}  (block node)")

def dump_tree(seq, indent="  ", max_depth=4, depth=0):
    if depth >= max_depth:
        return
    for i, node in enumerate(seq):
        safe_print(f"{indent}[{i}] ", )
        dump_node_details(node, indent + "  ")
        if 'sequence' in node and depth < max_depth - 1:
            dump_tree(node['sequence'], indent + "    ", max_depth, depth + 1)
        if 'branches' in node and depth < max_depth - 1:
            for bname, bseq in node['branches'].items():
                safe_print(f"{indent}    Branch [{bname}] ({len(bseq)} nodes):")
                dump_tree(bseq, indent + "      ", max_depth, depth + 1)

# VHN_fixing.json - find "Sheet Product" block
print("=" * 80)
print("  VHN_fixing.json - Sheet Product block (the product retrieval pipeline)")
print("=" * 80)

fixing = load_json(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_fixing.json')
all_fixing = find_all_nodes_with_path(fixing.get('sequence', []))

for path, node in all_fixing:
    if node.get('name') == 'Sheet Product':
        safe_print(f"\nFound at: {path}")
        if 'sequence' in node:
            dump_tree(node['sequence'], "  ", max_depth=5)

# Also dump node right AFTER Sheet Product block
print("\n\n" + "=" * 80)
print("  VHN_fixing.json - Nodes AFTER Sheet Product (how data is used in reply)")
print("=" * 80)

for path, node in all_fixing:
    if node.get('name') == 'Sheet Product':
        # Find parent sequence and index
        parts = path.split('.')
        # The Sheet Product block is inside a branch, find sibling nodes
        pass

# Find the Format Product Info or equivalent
for path, node in all_fixing:
    name = node.get('name', '').lower()
    if 'format' in name and 'product' in name:
        safe_print(f"\nFormat node: {path}")
        safe_print(f"Name: {node.get('name')}")
        dump_node_details(node, "  ")

# Find nodes that use api_call_product_data or api_raw_product_data
print("\n\n" + "=" * 80)
print("  VHN_fixing.json - Nodes referencing api data variables")
print("=" * 80)

for path, node in all_fixing:
    for key in ['instruction', 'expression', 'varValue', 'knowledge']:
        val = node.get('properties', {}).get(key, '')
        if 'api_call_product_data' in val or 'api_raw_product_data' in val or 'product_analyze' in val:
            safe_print(f"\n  Path: {path}")
            safe_print(f"  Name: {node.get('name')}")
            safe_print(f"  Type: {node.get('type')}")
            safe_print(f"  {key} (first 1000 chars):")
            safe_print(f"  {val[:1000]}")
            break

print("\n\n" + "=" * 80)
print("  VHN_DauTien_Fixed.json - Same analysis")
print("=" * 80)

fixed = load_json(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json')
all_fixed = find_all_nodes_with_path(fixed.get('sequence', []))

for path, node in all_fixed:
    for key in ['instruction', 'expression', 'varValue', 'knowledge']:
        val = node.get('properties', {}).get(key, '')
        if 'api_call_product_data' in val or 'api_raw_product_data' in val or 'product_analyze' in val:
            safe_print(f"\n  Path: {path}")
            safe_print(f"  Name: {node.get('name')}")
            safe_print(f"  Type: {node.get('type')}")
            safe_print(f"  {key} (first 1000 chars):")
            safe_print(f"  {val[:1000]}")
            break
