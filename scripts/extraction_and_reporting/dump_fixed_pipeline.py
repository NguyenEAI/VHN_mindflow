"""
Dump the COMPLETE B2C consult product pipeline in VHN_DauTien_Fixed.json
to compare with VHN_fixing.json
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

# Find "If need product info" and dump ALL children completely
print("=" * 80)
print("VHN_DauTien_Fixed.json - 'If need product info' branch [true] - ALL nodes")
print("=" * 80)

for path, node in all_nodes:
    if node.get('name') == 'If need product info':
        if 'branches' in node and 'true' in node['branches']:
            true_branch = node['branches']['true']
            for i, child in enumerate(true_branch):
                print(f"\n--- [{i}] ---")
                print(f"  type: {child.get('type')}")
                print(f"  name: {child.get('name')}")
                print(f"  id: {child.get('id')}")
                props = child.get('properties', {})
                for key in sorted(props.keys()):
                    val = str(props[key])
                    if len(val) > 3000:
                        val = val[:3000] + "..."
                    print(f"  {key}: {val}")
                    
                if 'branches' in child:
                    for bname, bseq in child['branches'].items():
                        print(f"\n  Branch [{bname}] ({len(bseq)} nodes):")
                        for j, gc in enumerate(bseq):
                            print(f"    [{j}] type={gc.get('type')}, name={gc.get('name')}")
                            gprops = gc.get('properties', {})
                            for key in sorted(gprops.keys()):
                                val = str(gprops[key])
                                if len(val) > 3000:
                                    val = val[:3000] + "..."
                                print(f"        {key}: {val}")

# Also find the B2C reply node that should use product_information
print("\n\n" + "=" * 80)
print("VHN_DauTien_Fixed.json - QnA nodes using product_information or product_analyze")
print("=" * 80)

for path, node in all_nodes:
    if node.get('type') == 'qna':
        inst = node.get('properties', {}).get('instruction', '')
        knowledge = node.get('properties', {}).get('knowledge', '')
        if 'product_information' in inst or 'product_information' in knowledge or 'product_analyze' in inst:
            print(f"\n  Path: {path}")
            print(f"  Name: {node.get('name')}")
            print(f"  varReply: {node.get('properties', {}).get('varReply')}")
            print(f"  knowledge: {knowledge}")
            print(f"  instruction (first 2000 chars):")
            print(f"  {inst[:2000]}")
