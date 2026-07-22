"""
COMPLETE dump of the B2C consult branch in both files.
We need to understand EVERY node in the sequence to find what's different.
"""
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def dump_node_tree(seq, indent="", max_depth=6, depth=0):
    if depth >= max_depth:
        return
    for i, node in enumerate(seq):
        t = node.get('type', '?')
        name = node.get('name', '?')
        nid = node.get('id', '?')
        props = node.get('properties', {})
        
        print(f"{indent}[{i}] type={t} | name={name} | id={nid}")
        
        # Key properties
        for key in ['varName', 'varValue', 'condition', 'varReply', 'api_response_var_name']:
            if key in props:
                print(f"{indent}     {key}={props[key]}")
        
        if t == 'qna':
            inst = props.get('instruction', '')
            # Check what variables it references
            refs = []
            for var in ['product_information', 'findproduct_data', 'product_wishlist', 'product_analyze']:
                if var in inst:
                    refs.append(var)
            if refs:
                print(f"{indent}     refs: {refs}")
            knowledge = props.get('knowledge', '')
            if knowledge:
                print(f"{indent}     knowledge={knowledge}")
        
        if 'sequence' in node:
            dump_node_tree(node['sequence'], indent + "  ", max_depth, depth + 1)
        if 'branches' in node:
            for bname, bseq in node['branches'].items():
                print(f"{indent}  Branch [{bname}] ({len(bseq)} nodes):")
                dump_node_tree(bseq, indent + "    ", max_depth, depth + 1)

# VHN_fixing.json - dump the product retrieval flow
print("=" * 80)
print("VHN_fixing.json - Product retrieval + reply flow")
print("=" * 80)

fixing = load_json(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_fixing.json')
# The product retrieval is in root[12]
seq = fixing.get('sequence', [])
print(f"\nTotal top-level nodes: {len(seq)}")
print("\nroot[12] (Sheet Product parent):")
if len(seq) > 12:
    dump_node_tree([seq[12]], "", max_depth=6)

print("\nroot[14] (Reply switch):")
if len(seq) > 14:
    dump_node_tree([seq[14]], "", max_depth=3)

# VHN_DauTien_Fixed.json - dump the B2C consult branch
print("\n\n" + "=" * 80)
print("VHN_DauTien_Fixed.json - B2C consult branch (COMPLETE)")  
print("=" * 80)

fixed = load_json(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json')
seq = fixed.get('sequence', [])
print(f"\nTotal top-level nodes: {len(seq)}")

# Find the switch node with b2c_consult branch
for i, node in enumerate(seq):
    if 'branches' in node and 'b2c_consult' in node.get('branches', {}):
        print(f"\nroot[{i}] (switch with b2c_consult):")
        b2c = node['branches']['b2c_consult']
        print(f"\n  b2c_consult branch ({len(b2c)} nodes):")
        dump_node_tree(b2c, "    ", max_depth=6)
        break
