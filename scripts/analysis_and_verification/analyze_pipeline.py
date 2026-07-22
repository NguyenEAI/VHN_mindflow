"""
Deep analysis: Compare the FULL product retrieval pipeline between
VHN_fixing.json and VHN_DauTien_Fixed.json.

Focus on:
1. What happens AFTER the API CALL returns data
2. How data flows into the reply prompt
3. The "Format Product Info" or equivalent node
4. Whether the bot is forced to ONLY use API data (no hallucination)
"""
import json

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

def dump_pipeline(data, label):
    print(f"\n{'='*80}")
    print(f"  {label}")
    print(f"{'='*80}")
    
    all_nodes = find_all_nodes_with_path(data.get('sequence', []))
    
    # Find all nodes in the product info pipeline
    # Look for: API CALL -> python/format -> QnA reply
    
    print("\n--- FULL NODE SEQUENCE after 'If need product info' ---")
    # Find the parent "If need product info" node and dump everything inside
    for path, node in all_nodes:
        if node.get('name') == 'If need product info' or node.get('id') == 'b2c_consult_product_if':
            print(f"\n  Found at: {path}")
            # Dump all children
            if 'branches' in node:
                for bname, bseq in node['branches'].items():
                    print(f"\n  Branch [{bname}]:")
                    for j, child in enumerate(bseq):
                        print(f"    [{j}] type={child.get('type')}, name={child.get('name')}, id={child.get('id')}")
                        if child.get('type') == 'qna':
                            print(f"        varReply={child.get('properties', {}).get('varReply')}")
                            inst = child.get('properties', {}).get('instruction', '')
                            print(f"        instruction (first 500 chars):")
                            print(f"        {inst[:500]}")
                            print(f"        knowledge={child.get('properties', {}).get('knowledge', '')}")
                        elif child.get('type') == 'python':
                            print(f"        varName={child.get('properties', {}).get('varName')}")
                            expr = child.get('properties', {}).get('expression', '')
                            print(f"        expression (first 500 chars):")
                            print(f"        {expr[:500]}")
                        elif child.get('type') == 'setVar':
                            print(f"        varName={child.get('properties', {}).get('varName')}")
                            print(f"        varValue={child.get('properties', {}).get('varValue')}")
                        elif child.get('type') == 'botAPICall':
                            print(f"        api_url={child.get('properties', {}).get('api_url')}")
                            print(f"        api_body={child.get('properties', {}).get('api_body')}")
                            print(f"        api_response_var_name={child.get('properties', {}).get('api_response_var_name')}")
                        elif child.get('type') == 'if':
                            print(f"        condition={child.get('properties', {}).get('condition')}")
                            if 'branches' in child:
                                for bn, bs in child['branches'].items():
                                    print(f"        Branch [{bn}] ({len(bs)} nodes):")
                                    for k, grandchild in enumerate(bs):
                                        print(f"          [{k}] type={grandchild.get('type')}, name={grandchild.get('name')}")
                                        if grandchild.get('type') == 'qna':
                                            inst2 = grandchild.get('properties', {}).get('instruction', '')
                                            print(f"              varReply={grandchild.get('properties', {}).get('varReply')}")
                                            print(f"              instruction (first 500 chars):")
                                            print(f"              {inst2[:500]}")
                                            print(f"              knowledge={grandchild.get('properties', {}).get('knowledge', '')}")
                                        elif grandchild.get('type') == 'python':
                                            print(f"              varName={grandchild.get('properties', {}).get('varName')}")
                                            expr2 = grandchild.get('properties', {}).get('expression', '')
                                            print(f"              expression (first 800 chars):")
                                            print(f"              {expr2[:800]}")
                                        elif grandchild.get('type') == 'setVar':
                                            print(f"              varName={grandchild.get('properties', {}).get('varName')}")
                                            print(f"              varValue={grandchild.get('properties', {}).get('varValue')}")
                                        elif grandchild.get('type') == 'botAPICall':
                                            print(f"              api_url={grandchild.get('properties', {}).get('api_url')}")
                                            print(f"              api_body={grandchild.get('properties', {}).get('api_body')}")
                                            print(f"              api_response_var_name={grandchild.get('properties', {}).get('api_response_var_name')}")

    # Also look for "Format Product Info" or similar nodes anywhere
    print(f"\n\n--- All 'Format' related nodes ---")
    for path, node in all_nodes:
        name = node.get('name', '')
        if 'format' in name.lower() or 'product' in name.lower():
            print(f"  Path: {path}")
            print(f"  Name: {name}")
            print(f"  Type: {node.get('type')}")
            if node.get('type') == 'qna':
                inst = node.get('properties', {}).get('instruction', '')
                print(f"  varReply: {node.get('properties', {}).get('varReply')}")
                print(f"  knowledge: {node.get('properties', {}).get('knowledge', '')}")
                print(f"  instruction (full):")
                print(inst)
            elif node.get('type') == 'python':
                print(f"  varName: {node.get('properties', {}).get('varName')}")
                print(f"  expression (full):")
                print(node.get('properties', {}).get('expression', ''))
            print()

# Run
for label, path in [
    ("VHN_fixing.json (WORKING)", r'C:\Users\Administrator\Desktop\Hoc_python\VHN_fixing.json'),
    ("VHN_DauTien_Fixed.json (BROKEN)", r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json'),
]:
    data = load_json(path)
    dump_pipeline(data, label)
